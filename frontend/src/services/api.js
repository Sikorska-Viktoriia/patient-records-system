import axios from 'axios';

const API_URL = 'http://localhost:8000';

export default {
    // Отримати список усіх пацієнтів
    async getPatients() {
        const response = await axios.get(`${API_URL}/patients/`);
        return response.data;
    },

    // Зареєструвати нового пацієнта
    async createPatient(patientData) {
        const response = await axios.post(`${API_URL}/patients/`, patientData);
        return response.data;
    },

    // Оновити медичні дані або статус (виписка/архівація)
    async updateMedicalRecord(id, medicalData) {
        const response = await axios.patch(`${API_URL}/patients/${id}/medical`, medicalData);
        return response.data;
    },

    // Видалити пацієнта
    async deletePatient(id) {
        await axios.delete(`${API_URL}/patients/${id}`);
    }
};