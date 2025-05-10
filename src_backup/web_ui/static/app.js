new Vue({
    el: '#app',
    vuetify: new Vuetify({
        theme: {
            themes: {
                light: {
                    primary: '#1976D2',
                    secondary: '#424242',
                    accent: '#82B1FF',
                    error: '#FF5252',
                    info: '#2196F3',
                    success: '#4CAF50',
                    warning: '#FFC107'
                }
            }
        }
    }),
    data: {
        drawer: true,
        services: {},
        selectedService: null,
        showSettings: false,
        showServiceDialog: false,
        showDeleteDialog: false,
        editedIndex: -1,
        editedService: {
            id: '',
            name: '',
            url: '',
            description: '',
            icon: 'mdi-web'
        },
        defaultService: {
            id: '',
            name: '',
            url: '',
            description: '',
            icon: 'mdi-web'
        },
        serviceHeaders: [
            { text: 'Name', value: 'name' },
            { text: 'URL', value: 'url' },
            { text: 'Beschreibung', value: 'description' },
            { text: 'Aktionen', value: 'actions', sortable: false }
        ],
        snackbar: {
            show: false,
            text: '',
            color: 'success'
        }
    },
    computed: {
        servicesArray() {
            return Object.keys(this.services).map(key => {
                return {
                    id: key,
                    ...this.services[key]
                };
            });
        }
    },
    created() {
        this.fetchServices();
    },
    methods: {
        async fetchServices() {
            try {
                const response = await axios.get('/api/services');
                this.services = response.data;
            } catch (error) {
                console.error('Fehler beim Laden der Dienste:', error);
                this.showSnackbar('Fehler beim Laden der Dienste', 'error');
            }
        },
        openService(service) {
            this.selectedService = service;
        },
        refreshIframe() {
            if (this.$refs.serviceFrame) {
                this.$refs.serviceFrame.src = this.selectedService.url;
            }
        },
        editService(item) {
            this.editedIndex = this.servicesArray.indexOf(item);
            this.editedService = Object.assign({}, item);
            this.showServiceDialog = true;
        },
        deleteService(item) {
            this.editedIndex = this.servicesArray.indexOf(item);
            this.editedService = Object.assign({}, item);
            this.showDeleteDialog = true;
        },
        async confirmDelete() {
            try {
                await axios.delete(`/api/services/${this.editedService.id}`);
                this.showSnackbar(`Dienst "${this.editedService.name}" wurde gelöscht`, 'success');
                this.fetchServices();
            } catch (error) {
                console.error('Fehler beim Löschen des Dienstes:', error);
                this.showSnackbar('Fehler beim Löschen des Dienstes', 'error');
            }
            this.showDeleteDialog = false;
        },
        addNewService() {
            this.editedIndex = -1;
            this.editedService = Object.assign({}, this.defaultService);
            this.showServiceDialog = true;
        },
        closeServiceDialog() {
            this.showServiceDialog = false;
            this.$nextTick(() => {
                this.editedService = Object.assign({}, this.defaultService);
                this.editedIndex = -1;
            });
        },
        async saveService() {
            try {
                if (this.editedIndex > -1) {
                    // Dienst aktualisieren
                    await axios.put(`/api/services/${this.editedService.id}`, this.editedService);
                    this.showSnackbar(`Dienst "${this.editedService.name}" wurde aktualisiert`, 'success');
                } else {
                    // Neuen Dienst hinzufügen
                    await axios.post('/api/services', this.editedService);
                    this.showSnackbar(`Dienst "${this.editedService.name}" wurde hinzugefügt`, 'success');
                }
                this.fetchServices();
                this.closeServiceDialog();
            } catch (error) {
                console.error('Fehler beim Speichern des Dienstes:', error);
                this.showSnackbar('Fehler beim Speichern des Dienstes', 'error');
            }
        },
        showSnackbar(text, color = 'success') {
            this.snackbar.text = text;
            this.snackbar.color = color;
            this.snackbar.show = true;
        }
    }
});