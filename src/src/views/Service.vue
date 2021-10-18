<template>
  <div id="service">
    <v-simple-table class="mt-5" dark>
      <template v-slot:default>
        <thead>
          <tr color="primary">
            <th>service name</th>
            <th>status</th>
            <th>service mode</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th>{{ livestatus.chibasite.service_viewname }}</th>
            <th>
              <v-chip
                outlined
                v-bind:color="serviceStatusColor(livestatus.chibasite)"
              >
                {{ livestatus.chibasite.message }}
              </v-chip>
            </th>
            <th>
              <div v-show="isAuthenticated">
                <v-btn
                  v-show="isLiveChiba"
                  @click="requireServiceDead('chibasite')"
                  color="red"
                  outlined
                  :loading="isloading['chibasite']"
                  >Stop</v-btn
                >
                <v-btn
                  v-show="!isLiveChiba"
                  @click="requireServiceLive('chibasite')"
                  color="yellow"
                  :loading="isloading['chibasite']"
                  >Start</v-btn
                >
              </div>
              <div v-show="!isAuthenticated">---</div>
            </th>
          </tr>
          <tr>
            <th>{{ livestatus.rsite.service_viewname }}</th>
            <th>
              <v-chip
                outlined
                v-bind:color="serviceStatusColor(livestatus.rsite)"
              >
                {{ livestatus.rsite.message }}
              </v-chip>
            </th>
            <th>---</th>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
    <div class="py-5">
      <v-alert v-show="message" type="error" elevation="12">{{ message }}</v-alert>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'Service',
  data () {
    return {
      message: '',
      isloading: { chibasite: false, rsite: false }
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated', '']),
    ...mapGetters('service', ['livestatus']),
    isLiveChiba () { return this.livestatus.chibasite.statusCode === 200 }
  },
  methods: {
    ...mapActions('service', ['fetchLiveStatus', 'requireServiceMode']),
    serviceStatusColor (v) {
      return v.statusCode === 200 ? 'green' : 'red'
    },
    requireServiceLive (serviceName) {
      this.isloading[serviceName] = true
      this.requireServiceMode({ mode: 'up', target: serviceName })
        .catch(error => (this.message = error))
        .finally(this.isloading[serviceName] = false)
    },
    requireServiceDead (serviceName) {
      this.isloading[serviceName] = true
      this.requireServiceMode({ mode: 'down', target: serviceName })
        .catch(error => (this.message = error))
        .finally(this.isloading[serviceName] = false)
    }
  },
  created: function () {
    this.fetchLiveStatus('chibasite')
      .catch(error => (this.message = error))
    this.fetchLiveStatus('rsite')
      .catch(error => (this.message = error))
  }
}
</script>
