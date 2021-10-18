<template>
  <div id="schedule">
    <h1>Schedule list</h1>
    <v-row>
      <v-col>
        <v-alert v-show="message" border="left" color="orange" elevation="12">{{ message }}</v-alert>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <schedule-list
          v-bind:name="schedules.chibasite.service_viewname"
          v-bind:daylist="schedules.chibasite.data"
          @booking="bookingChiba"
        >
        </schedule-list>
      </v-col>
      <v-col>
        <schedule-list
          v-bind:name="schedules.rsite.service_viewname"
          v-bind:daylist="schedules.rsite.data"
          @booking="bookingRsite"
        >
        </schedule-list>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import ScheduleList from '../components/ScheduleList'

export default {
  name: 'Schedules',
  data: function () {
    return {
      isloding: false,
      message: ''
    }
  },
  computed: {
    ...mapGetters('schedules', ['schedules'])
  },
  methods: {
    ...mapActions('schedules', ['fetchSchedules', 'booking']),
    notifyMessage (v) {
      this.message = v.message
    },
    bookingChiba (v) {
      this.booking({ target: 'chibasite', date: v.date })
        .catch(error => (this.message = error))
    },
    bookingRsite (v) {
      this.booking({ target: 'rsite', date: v.date })
        .then(response => (this.message = response.message))
        .catch(error => (this.message = error))
    }
  },
  created: function () {
    this.fetchSchedules()
  },
  components: {
    ScheduleList
  }
}
</script>
