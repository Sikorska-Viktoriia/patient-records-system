<script setup>
import { ref, onMounted, computed } from 'vue';
import api from './services/api.js'; 
const patients = ref([]);
const currentTab = ref('register'); 
const selectedPatient = ref(null); 
const error = ref('');


const searchQuery = ref('');


const showArchiveModal = ref(false);
const patientToArchive = ref(null);
const dischargeForm = ref({
  discharge_date: new Date().toISOString().split('T')[0],
  additional_notes: ''
});

// Форма реєстрації нового пацієнта
const form = ref({
  last_name: '', first_name: '', middle_name: '', gender: 'Чоловіча', birth_date: '',
  contact: { phone: '', address: '' },
  emergency_contact: { name: '', phone: '', relationship_type: '' },
  medical_record: { admission_date: '', admission_diagnosis: '', symptoms: '' }
});

// Форма редагування на детальній сторінці
const editMedicalForm = ref({
  blood_type: '',
  allergies: '',
  contraindications: '',
  additional_notes: '',
  discharge_date: ''
});

const loadPatients = async () => {
  try {
    patients.value = await api.getPatients();
  } catch (err) {
    console.error('Помилка завантаження пацієнтів:', err);
  }
};

// Список активних пацієнтів із фільтрацією за ПІБ або телефоном
const filteredActivePatients = computed(() => {
  const active = patients.value.filter(p => (p.medical_record?.status || 'active') === 'active');
  if (!searchQuery.value.trim()) return active;
  
  const q = searchQuery.value.toLowerCase();
  return active.filter(p => {
    const fullName = `${p.last_name} ${p.first_name} ${p.middle_name || ''}`.toLowerCase();
    const phone = p.contact?.phone?.toLowerCase() || '';
    return fullName.includes(q) || phone.includes(q);
  });
});

// Список архівованих пацієнтів
const archivedPatients = computed(() => {
  return patients.value.filter(p => p.medical_record?.status === 'archived');
});

const handleSubmit = async () => {
  try {
    error.value = '';
    const birthYear = new Date(form.value.birth_date).getFullYear();
    if (birthYear > new Date().getFullYear() || birthYear < 1900) {
      error.value = 'Введено неможливу дату народження!';
      return;
    }

    await api.createPatient(form.value);
    
    // Очищення форми
    form.value = {
      last_name: '', first_name: '', middle_name: '', gender: 'Чоловіча', birth_date: '',
      contact: { phone: '', address: '' },
      emergency_contact: { name: '', phone: '', relationship_type: '' },
      medical_record: { admission_date: '', admission_diagnosis: '', symptoms: '' }
    };
    
    alert('Пацієнта успішно зареєстровано!');
    currentTab.value = 'patients';
    await loadPatients();
  } catch (err) {
    error.value = err.response?.data?.detail || 'Помилка при створенні пацієнта';
  }
};

const openPatientDetails = (patient) => {
  selectedPatient.value = patient;
  editMedicalForm.value = {
    blood_type: patient.medical_record?.blood_type || '',
    allergies: patient.medical_record?.allergies || '',
    contraindications: patient.medical_record?.contraindications || '',
    additional_notes: patient.medical_record?.additional_notes || '',
    discharge_date: patient.medical_record?.discharge_date || ''
  };
};

const saveMedicalDetails = async () => {
  try {
    error.value = '';
    const patientId = selectedPatient.value.id;
    const payload = {
      blood_type: editMedicalForm.value.blood_type || null,
      allergies: editMedicalForm.value.allergies || null,
      contraindications: editMedicalForm.value.contraindications || null,
      additional_notes: editMedicalForm.value.additional_notes || null,
      discharge_date: editMedicalForm.value.discharge_date || null,
      status: editMedicalForm.value.discharge_date ? 'archived' : 'active'
    };

    await api.updateMedicalRecord(patientId, payload);
    await loadPatients();
    
    alert('Медичні дані успішно оновлено!');
    selectedPatient.value = null;
  } catch (err) {
    error.value = err.response?.data?.detail || 'Помилка збереження';
  }
};

const openArchiveModal = (patient) => {
  patientToArchive.value = patient;
  dischargeForm.value = {
    discharge_date: new Date().toISOString().split('T')[0],
    additional_notes: patient.medical_record?.additional_notes || ''
  };
  showArchiveModal.value = true;
};

const confirmArchive = async () => {
  try {
    if (!dischargeForm.value.discharge_date) {
      alert('Будь ласка, введіть дату виписки!');
      return;
    }

    await api.updateMedicalRecord(patientToArchive.value.id, {
      discharge_date: dischargeForm.value.discharge_date,
      additional_notes: dischargeForm.value.additional_notes,
      status: 'archived'
    });

    showArchiveModal.value = false;
    patientToArchive.value = null;
    await loadPatients();
  } catch (err) {
    alert(err.response?.data?.detail || 'Помилка архівації пацієнта');
  }
};

onMounted(() => {
  loadPatients();
});
</script>

<template>
  <div class="app-wrapper">
    <div class="container">
      <header class="app-header">
        <div class="logo-badge">🏥</div>
        <h1>Електронна система медичних карт пацієнтів</h1>
      </header>

      <!-- ПАНЕЛЬ ВКЛАДОК -->
      <div class="tabs">
        <button :class="{ active: currentTab === 'register' }" @click="currentTab = 'register'; selectedPatient = null;">
          <span>➕</span> Реєстрація
        </button>
        <button :class="{ active: currentTab === 'patients' }" @click="currentTab = 'patients'; selectedPatient = null;">
          <span>📋</span> Список карт та пошук
        </button>
        <button :class="{ active: currentTab === 'archive' }" @click="currentTab = 'archive'; selectedPatient = null;">
          <span>📁</span> Архів
        </button>
      </div>

      <!-- ДЕТАЛЬНА МЕДИЧНА КАРТА -->
      <div v-if="selectedPatient" class="card detail-page">
        <button @click="selectedPatient = null" class="back-btn">⬅ Назад до списку</button>
        <h2>📄 Медична картка пацієнта</h2>
        
        <div class="patient-summary">
          <h3>{{ selectedPatient.last_name }} {{ selectedPatient.first_name }} {{ selectedPatient.middle_name }}</h3>
          <div class="summary-grid">
            <p><strong>Стать:</strong> {{ selectedPatient.gender }}</p>
            <p><strong>Дата народження:</strong> {{ selectedPatient.birth_date }}</p>
            <p><strong>Телефон:</strong> {{ selectedPatient.contact?.phone }}</p>
            <p><strong>Адреса:</strong> {{ selectedPatient.contact?.address || 'Не вказана' }}</p>
          </div>
          <p><strong>Екстрений контакт:</strong> {{ selectedPatient.emergency_contact?.name }} ({{ selectedPatient.emergency_contact?.relationship_type }}) — 📞 {{ selectedPatient.emergency_contact?.phone }}</p>
          <hr class="divider">
          <div class="summary-grid">
            <p><strong>Дата госпіталізації:</strong> {{ selectedPatient.medical_record?.admission_date }}</p>
            <p v-if="selectedPatient.medical_record?.discharge_date"><strong>Дата виписки:</strong> {{ selectedPatient.medical_record.discharge_date }}</p>
          </div>
          <p><strong>Первинний діагноз:</strong> {{ selectedPatient.medical_record?.admission_diagnosis }}</p>
          <p><strong>Симптоми:</strong> {{ selectedPatient.medical_record?.symptoms || 'Не вказані' }}</p>
        </div>

        <div class="edit-medical-section">
          <h3>⚙️ Розширені медичні дані та виписка</h3>
          
          <div class="form-grid">
            <div>
              <label class="input-label">Група крові:</label>
              <input v-model="editMedicalForm.blood_type" placeholder="Наприклад: A(II)+, O(I)-" />
            </div>
            <div>
              <label class="input-label">Дата виписки (автоматично переводить в архів):</label>
              <input type="date" v-model="editMedicalForm.discharge_date" class="date-input" />
            </div>
          </div>

          <label class="input-label">Алергічні реакції:</label>
          <textarea v-model="editMedicalForm.allergies" placeholder="Вкажіть алергії..."></textarea>

          <label class="input-label">Медичні протипоказання:</label>
          <textarea v-model="editMedicalForm.contraindications" placeholder="Протипоказання до препаратів..."></textarea>

          <label class="input-label">Додаткові нотатки лікаря:</label>
          <textarea v-model="editMedicalForm.additional_notes" placeholder="Примітки епікризу..."></textarea>

          <button @click="saveMedicalDetails" class="submit-btn" style="margin-top: 15px;">Зберегти зміни</button>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
      </div>


      <div v-else>

        <!-- ВКЛАДКА 1: РЕЄСТРАЦІЯ -->
        <div v-if="currentTab === 'register'" class="card">
          <h2>➕ Реєстрація нового пацієнта</h2>
          <form @submit.prevent="handleSubmit" class="patient-form">
            <div class="form-grid">
              <div class="form-section">
                <h3>Особисті дані</h3>
                <div class="input-group">
                  <input v-model="form.last_name" placeholder="Прізвище" required />
                  <input v-model="form.first_name" placeholder="Ім'я" required />
                  <input v-model="form.middle_name" placeholder="По батькові" />
                  <select v-model="form.gender">
                    <option value="Чоловіча">Чоловіча</option>
                    <option value="Жіноча">Жіноча</option>
                  </select>
                  <div>
                    <label class="input-label">Дата народження:</label>
                    <input type="date" v-model="form.birth_date" class="date-input" required />
                  </div>
                </div>
              </div>

              <div class="form-section">
                <h3>Контакти та екстрений зв'язок</h3>
                <div class="input-group">
                  <input v-model="form.contact.phone" placeholder="Телефон (+380...)" required />
                  <input v-model="form.contact.address" placeholder="Домашня адреса" />
                  <input v-model="form.emergency_contact.name" placeholder="ПІБ контактної особи (Emergency)" required />
                  <input v-model="form.emergency_contact.phone" placeholder="Телефон екстреного контакту" required />
                  <input v-model="form.emergency_contact.relationship_type" placeholder="Ким доводиться (напр. дружина)" />
                </div>
              </div>
            </div>

            <div class="form-section full-width">
              <h3>Госпіталізація та діагноз</h3>
              <div class="hospital-grid">
                <div>
                  <label class="input-label">Дата госпіталізації:</label>
                  <input type="date" v-model="form.medical_record.admission_date" class="date-input" required />
                </div>
                <div>
                  <label class="input-label">Первинний діагноз:</label>
                  <input v-model="form.medical_record.admission_diagnosis" placeholder="Введіть первинний діагноз" required />
                </div>
              </div>
              <label class="input-label" style="margin-top: 15px;">Симптоми та скарги:</label>
              <textarea v-model="form.medical_record.symptoms" placeholder="Опишіть симптоми та скарги пацієнта..."></textarea>
            </div>

            <button type="submit" class="submit-btn">Зареєструвати пацієнта</button>
          </form>
          <p v-if="error" class="error">{{ error }}</p>
        </div>

        <!-- ВКЛАДКА 2: СПИСОК КАРТ ТА ПОШУК -->
        <div v-if="currentTab === 'patients'" class="card">
          <h2>📋 Список карт активних пацієнтів та пошук</h2>
          
          <div class="search-box">
            <input v-model="searchQuery" placeholder="🔍 Швидкий пошук за ПІБ або номером телефону..." class="search-input" />
          </div>

          <p v-if="filteredActivePatients.length === 0" class="empty-text">Пацієнтів не знайдено.</p>
          
          <div v-else class="patient-list">
            <div v-for="patient in filteredActivePatients" :key="patient.id" class="patient-card">
              <div class="patient-info">
                <strong>{{ patient.last_name }} {{ patient.first_name }} {{ patient.middle_name }}</strong> 
                <span class="birth-year">(Нар: {{ patient.birth_date }})</span><br>
                <small>📞 {{ patient.contact?.phone }} &nbsp;|&nbsp; 🩺 Діагноз: <b>{{ patient.medical_record?.admission_diagnosis }}</b></small>
              </div>
              <div class="patient-actions">
                <button @click="openPatientDetails(patient)" class="details-btn">📂 Мед. картка</button>
                <button @click="openArchiveModal(patient)" class="archive-btn">📁 В архів</button>
              </div>
            </div>
          </div>
        </div>

        <!-- ВКЛАДКА 3: АРХІВ -->
        <div v-if="currentTab === 'archive'" class="card">
          <h2>📁 Архів виписаних пацієнтів</h2>
          <p v-if="archivedPatients.length === 0" class="empty-text">Архів порожній.</p>
          
          <div v-else class="patient-list">
            <div v-for="patient in archivedPatients" :key="patient.id" class="patient-card archived-card">
              <div class="patient-info">
                <strong>{{ patient.last_name }} {{ patient.first_name }} {{ patient.middle_name }}</strong> 
                <span class="birth-year">(Виписано: {{ patient.medical_record?.discharge_date }})</span><br>
                <small>📞 {{ patient.contact?.phone }} &nbsp;|&nbsp; 🩺 Діагноз: <b>{{ patient.medical_record?.admission_diagnosis }}</b></small>
              </div>
              <div class="patient-actions">
                <button @click="openPatientDetails(patient)" class="details-btn">📂 Переглянути картку</button>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- МОДАЛЬНЕ ВІКНО ДЛЯ АРХІВАЦІЇ -->
      <div v-if="showArchiveModal" class="modal-backdrop">
        <div class="modal-content">
          <h3>📁 Виписка пацієнта в архів</h3>
          <p class="modal-desc">Оберіть дату виписки для пацієнта <strong>{{ patientToArchive?.last_name }} {{ patientToArchive?.first_name }}</strong>:</p>
          
          <label class="input-label">Дата виписки:</label>
          <input type="date" v-model="dischargeForm.discharge_date" class="date-input modal-input" required />

          <label class="input-label">Примітки / Епікриз виписки:</label>
          <textarea v-model="dischargeForm.additional_notes" class="modal-textarea" placeholder="Коментар при виписці..."></textarea>

          <div class="modal-actions">
            <button @click="confirmArchive" class="submit-btn modal-confirm">Підтвердити виписку</button>
            <button @click="showArchiveModal = false" class="modal-cancel">Скасувати</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.app-wrapper {
  background-color: #f0f4f1;
  min-height: 100vh;
  padding: 40px 20px;
  box-sizing: border-box;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #2c3e50;
}

.app-header {
  margin-bottom: 30px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.logo-badge {
  font-size: 32px;
  background: #e8f5e9;
  padding: 10px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(46, 125, 50, 0.1);
}

.app-header h1 {
  font-size: 28px;
  color: #1b5e20;
  margin: 0;
  font-weight: 700;
}

h2, h3 {
  color: #2c3e50;
}

/* Вкладки */
.tabs {
  margin-bottom: 25px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.tabs button {
  padding: 12px 24px;
  cursor: pointer;
  border: 1px solid #dcedc8;
  background: #ffffff;
  color: #333333;
  border-radius: 8px;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  display: flex;
  align-items: center;
  gap: 8px;
}
.tabs button.active {
  background: #2e7d32;
  color: #ffffff;
  border-color: #2e7d32;
  box-shadow: 0 4px 12px rgba(46, 125, 50, 0.2);
}
.tabs button:hover:not(.active) {
  background: #f1f8e9;
}

/* Картки та сітки */
.card {
  background: #ffffff;
  padding: 35px;
  border-radius: 16px;
  margin-bottom: 30px;
  box-shadow: 0 10px 30px rgba(46, 125, 50, 0.05);
  border: 1px solid #e2ece3;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
}

@media (max-width: 768px) {
  .form-grid, .hospital-grid, .summary-grid {
    grid-template-columns: 1fr !important;
  }
}

.hospital-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.form-section {
  background: #fafbfc;
  padding: 24px;
  margin-bottom: 20px;
  border-radius: 12px;
  border: 1px solid #edf2f7;
}

.form-section.full-width {
  grid-column: span 2;
}

.form-section h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 17px;
  color: #2e7d32;
  border-bottom: 2px solid #e8f5e9;
  padding-bottom: 8px;
}

/* Елементи форм та пошук */
.input-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 6px;
  margin-top: 12px;
}

input, select, textarea, .search-input {
  display: block;
  width: 100%;
  margin-bottom: 14px;
  padding: 12px 14px;
  box-sizing: border-box;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  background: #ffffff;
  color: #2d3748;
  font-size: 14px;
  transition: all 0.2s;
}

input:focus, select:focus, textarea:focus, .search-input:focus {
  border-color: #2e7d32;
  outline: none;
  box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.12);
}

textarea {
  resize: vertical;
  min-height: 90px;
}

.date-input::-webkit-calendar-picker-indicator {
  cursor: pointer;
  filter: invert(0.3) sepia(1) saturate(5) hue-rotate(90deg);
}

/* Кнопки */
.submit-btn {
  background: #2e7d32;
  color: #ffffff;
  border: none;
  padding: 14px;
  width: 100%;
  cursor: pointer;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  transition: background 0.2s, transform 0.1s;
  box-shadow: 0 4px 12px rgba(46, 125, 50, 0.2);
}
.submit-btn:hover {
  background: #1b5e20;
}
.submit-btn:active {
  transform: scale(0.99);
}

.error {
  color: #e53e3e;
  margin-top: 12px;
  font-weight: 500;
}

/* Список пацієнтів */
.patient-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.patient-card {
  background: #ffffff;
  padding: 20px 24px;
  border-radius: 10px;
  border: 1px solid #e2ece3;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 6px rgba(0,0,0,0.01);
  transition: transform 0.2s, box-shadow 0.2s;
}
.patient-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.05);
}
.archived-card {
  border-color: #cbd5e0;
  background: #f8fafc;
}

.patient-info strong {
  font-size: 16px;
  color: #1a202c;
}
.birth-year {
  color: #718096;
  font-size: 13px;
}
.patient-info small {
  color: #4a5568;
  display: inline-block;
  margin-top: 6px;
}

.patient-actions {
  display: flex;
  gap: 10px;
}
.patient-actions button {
  padding: 9px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  transition: opacity 0.2s;
}
.details-btn {
  background: #c8e6c9;
  color: #1b5e20;
}
.details-btn:hover {
  background: #a5d6a7;
}
.archive-btn {
  background: #fff9c4;
  color: #f57f17;
}
.archive-btn:hover {
  background: #fff176;
}

.back-btn {
  background: #edf2f7;
  color: #4a5568;
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 20px;
  font-weight: 600;
  transition: background 0.2s;
}
.back-btn:hover {
  background: #e2e8f0;
}

.patient-summary, .edit-medical-section {
  background: #f8fafc;
  padding: 30px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  margin-bottom: 25px;
}
.divider {
  border: 0;
  border-top: 1px solid #cbd5e0;
  margin: 20px 0;
}

.empty-text {
  color: #a0aec0;
  text-align: center;
  padding: 20px;
}

/* Модальне вікно */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}
.modal-content {
  background: #ffffff;
  padding: 35px;
  border-radius: 16px;
  width: 450px;
  max-width: 90%;
  box-shadow: 0 15px 35px rgba(0,0,0,0.2);
  border: 1px solid #e2e8f0;
}
.modal-desc {
  color: #4a5568;
  font-size: 14px;
  margin-bottom: 20px;
}
.modal-input, .modal-textarea {
  display: block;
  width: 100%;
  margin-bottom: 15px;
  padding: 12px 14px;
  box-sizing: border-box;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
}
.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 25px;
}
.modal-confirm {
  flex: 1;
}
.modal-cancel {
  background: #edf2f7;
  color: #4a5568;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}
.modal-cancel:hover {
  background: #e2e8f0;
}
</style>