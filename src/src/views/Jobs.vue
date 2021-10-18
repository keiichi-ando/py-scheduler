<template>
    <div id="schedule">
        <h1>Scheduled jobs</h1>
        <job-list v-bind:joblist="jobs" />
        <div class="pt-5" v-show="isAuthenticated">
          <v-btn outlined elevation="2" @click="requireResetJobs" color="warning" :loading="isloading">
            <v-icon>mdi-reload-alert</v-icon>
            JOB再セット
          </v-btn>
        </div>
      <div class="py-5">
        <v-alert v-show="message" border="left" color="orange" elevation="12">{{ message }}</v-alert>
      </div>
    </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import JobList from '../components/JobList'

export default {
  name: 'Jobs',
  data: () => ({
    message: '',
    isloading: false
  }),
  computed: {
    ...mapGetters(['isAuthenticated']),
    ...mapGetters('schedules', ['jobs'])
  },
  methods: {
    ...mapActions('schedules', ['fetchJobs', 'resetJobs']),
    requireResetJobs () {
      this.isloading = true
      this.resetJobs()
        .then(response => (this.message = response.message))
        .catch(error => (this.message = error))
        .finally(() => (this.isloading = false))
    }
  },
  created: function () {
    this.fetchJobs()
  },
  components: {
    JobList
  }
}
</script>
