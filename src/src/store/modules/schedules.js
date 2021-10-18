import axios from 'axios'

const state = {
  schedules: { chibasite: {}, rsite: {} },
  jobs: []
}

const getters = {
  schedules: state => state.schedules,
  jobs: state => state.jobs
}

const mutations = {
  setSchedules: (state, schedules) => (state.schedules = schedules.data.schedules),
  setJobs: (state, jobs) => (state.jobs = jobs.data)
}

const actions = {
  async fetchSchedules ({ commit }) {
    const response = await axios.get('/api/schedules/daylist')
    commit('setSchedules', response.data)
  },
  async fetchJobs ({ commit }) {
    const response = await axios.get('/api/schedules/joblist')
    commit('setJobs', response.data)
  },
  async resetJobs ({ commit }) {
    return new Promise((resolve, reject) => {
      axios.defaults.headers.common = { Authorization: `Bearer ${this.state.userToken}` }
      axios.post('/api/schedules/jobs/reset')
        .then(response => {
          commit('setJobs', response.data)
          resolve(response.data)
        })
        .catch(error => reject(error))
    })
  },
  async booking ({ commit }, payload) {
    return new Promise((resolve, reject) => {
      axios.defaults.headers.common = { Authorization: `Bearer ${this.state.userToken}` }
      axios.post(`/api/schedules/booking/${payload.target}`, { date: payload.date })
        .then(response => {
          resolve(response.data)
          commit('setSchedules', response.data)
        })
        .catch(error => reject(error))
    })
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
