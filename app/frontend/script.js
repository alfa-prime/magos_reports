const { createApp, ref } = Vue;

createApp({
    setup() {
        // --- КОНФИГУРАЦИЯ ---
        const BACKEND_URL = '';
        const API_KEY = 'vmqZThci10eteSqy7dfF3FypJhV7grC6coCDr87LsPg';

        // --- ДАННЫЕ ---
        const reports = ref([
            {
                id: '32430',
                name: 'Список пациентов с услугами по стационару',
                description: 'Список пациентов с услугами по стационару + тип оплаты'
            },
            {
                id: 'invitro',
                name: 'Анализы ИНВИТРО',
                description: 'Отчет по лабораторным исследованиям Инвитро +  тип оплаты.'
            }
        ]);

        const selectedReport = ref(null);

        // Даты по умолчанию (сегодня)
        const today = new Date().toISOString().split('T')[0];
        const startDate = ref(today);
        const endDate = ref(today);

        const isLoading = ref(false);
        const error = ref('');

        // --- МЕТОДЫ ---
        const selectReport = (report) => {
            selectedReport.value = report;
            error.value = '';
        };

        const download = async () => {
            if (!selectedReport.value) return;

            isLoading.value = true;
            error.value = '';

            try {
                // Превращаем 2025-11-27 -> 27.11.2025 для API
                const formatDate = (d) => d.split('-').reverse().join('.');

                const response = await axios.get(`${BACKEND_URL}/report/${selectedReport.value.id}`, {
                    params: {
                        start_date: formatDate(startDate.value),
                        end_date: formatDate(endDate.value)
                    },
                    responseType: 'blob', // Ждем файл
                    headers: {
                        'X-API-KEY': API_KEY
                    }
                });

                // Создаем ссылку и скачиваем
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;

                // Пытаемся достать имя файла из заголовков
                const disposition = response.headers['content-disposition'];
                let filename = `report_${selectedReport.value.id}.xlsx`;

                if (disposition && disposition.indexOf('filename=') !== -1) {
                    const matches = /filename="?([^"]+)"?/.exec(disposition);
                    if (matches != null && matches[1]) filename = matches[1];
                }

                link.setAttribute('download', filename);
                document.body.appendChild(link);
                link.click();
                link.remove();
                window.URL.revokeObjectURL(url);

            } catch (err) {
                console.error(err);
                // Если пришел Blob (файл), но внутри JSON с ошибкой
                if (err.response && err.response.data instanceof Blob) {
                    const reader = new FileReader();
                    reader.onload = () => {
                        try {
                            const json = JSON.parse(reader.result);
                            error.value = json.detail || 'Ошибка сервера';
                        } catch (e) {
                            error.value = 'Ошибка при скачивании файла';
                        }
                    };
                    reader.readAsText(err.response.data);
                } else {
                    error.value = 'Сервер недоступен (проверьте VPN или сеть)';
                }
            } finally {
                isLoading.value = false;
            }
        };

        return {
            reports,
            selectedReport,
            selectReport,
            startDate,
            endDate,
            isLoading,
            error,
            download
        };
    }
}).mount('#app');