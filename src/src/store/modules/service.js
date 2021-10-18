import axios from 'axios'

const state = {
  livestatus: { chibasite: {}, rsite: {} }
}

const getters = {
  livestatus: state => state.livestatus
}

const mutations = {
  setLiveStatus: (state, livestatus) => (state.livestatus[livestatus.data.status.service_name] = livestatus.data.status)
}

const actions = {
  async fetchLiveStatus ({ commit }, sitename) {
    return new Promise((resolve, reject) => {
      axios.get(`/api/service/state/${sitename}`)
        .then(response => commit('setLiveStatus', response.data))
        .catch(error => reject(error))
    })
  },
  async requireServiceMode ({ commit }, payload) {
    const mode = payload.mode
    const target = payload.target
    return new Promise((resolve, reject) => {
      axios.defaults.headers.common = { Authorization: `Bearer ${this.state.userToken}` }
      axios.post(`/api/service/${mode}/${target}`)
        .then(response => {
          commit('setLiveStatus', response.data)
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
