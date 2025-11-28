const { createApp, ref, reactive } = Vue;

createApp({
    setup() {
        const BACKEND_URL = '';
        const API_KEY = 'vmqZThci10eteSqy7dfF3FypJhV7grC6coCDr87LsPg';

        const reports = ref([
            {
              id: '32430',
              name: 'Список пациентов с услугами по стационару',
              description: 'Выгрузка списка пациентов по стационару с услугами и источником оплаты.'
            },
            {
              id: 'invitro',
              name: 'Анализы ИНВИТРО',
              description: 'Отчет по лабораторным исследованиям Инвитро + тип оплаты'
            }
        ]);

        const selectedReport = ref(null);
        const today = new Date().toISOString().split('T')[0];
        const startDate = ref(today);
        const endDate = ref(today);

        // Список активных загрузок
        const downloads = ref([]);

        const selectReport = (report) => {
            selectedReport.value = report;
        };

        // Хелпер для обновления статуса задачи в массиве
        const updateDownloadStatus = (id, status, message) => {
            const item = downloads.value.find(d => d.id === id);
            if (item) {
                item.status = status;
                item.message = message;
            }
        };

        const removeDownload = (id) => {
            downloads.value = downloads.value.filter(d => d.id !== id);
        };

        const download = async () => {
            if (!selectedReport.value) return;

            const reportId = selectedReport.value.id;
            const sDate = startDate.value;
            const eDate = endDate.value;

            // Генерируем ID для этой задачи
            const taskId = Date.now();

            // Создаем задачу и сразу кладем в реактивный массив
            downloads.value.unshift({
                id: taskId,
                name: selectedReport.value.name,
                status: 'loading',
                message: 'Формирование отчета...',
                startTime: new Date().toLocaleTimeString()
            });

            try {
                const formatDate = (d) => d.split('-').reverse().join('.');

                const response = await axios.get(`${BACKEND_URL}/report/${reportId}`, {
                    params: {
                        start_date: formatDate(sDate),
                        end_date: formatDate(eDate)
                    },
                    responseType: 'blob',
                    headers: { 'X-API-KEY': API_KEY }
                });

                // Скачивание
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;

                const disposition = response.headers['content-disposition'];
                let filename = `report_${reportId}.xlsx`;
                if (disposition && disposition.indexOf('filename=') !== -1) {
                    const matches = /filename="?([^"]+)"?/.exec(disposition);
                    if (matches != null && matches[1]) filename = matches[1];
                }

                link.setAttribute('download', filename);
                document.body.appendChild(link);
                link.click();
                link.remove();
                window.URL.revokeObjectURL(url);

                // ОБНОВЛЕНИЕ СТАТУСА (Через поиск в массиве)
                updateDownloadStatus(taskId, 'success', 'Готово! Файл скачан.');

                // Автоудаление через 5 сек
                setTimeout(() => removeDownload(taskId), 5000);

            } catch (err) {
                console.error(err);

                let errorMsg = 'Неизвестная ошибка';

                if (err.response && err.response.data instanceof Blob) {
                    const reader = new FileReader();
                    reader.onload = () => {
                        try {
                            const json = JSON.parse(reader.result);
                            errorMsg = json.detail || 'Ошибка сервера';
                        } catch {
                            errorMsg = 'Ошибка при чтении ответа';
                        }
                        // Обновляем статус внутри коллбэка чтения
                        updateDownloadStatus(taskId, 'error', errorMsg);
                    };
                    reader.readAsText(err.response.data);
                } else {
                    errorMsg = 'Сервер недоступен';
                    updateDownloadStatus(taskId, 'error', errorMsg);
                }
            }
        };

        return {
            reports,
            selectedReport,
            selectReport,
            startDate,
            endDate,
            downloads,
            download,
            removeDownload
        };
    }
}).mount('#app');