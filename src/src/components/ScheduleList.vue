<template>
  <v-card width="300px" dark>
    <v-card-title class="subheadign font-weight-bold">
      {{ name }}
    </v-card-title>
    <v-divider></v-divider>
    <v-list subheader>
      <v-list-item v-for="(holiday, date, index) in daylist" v-bind:key="index">
        <div class="row justify-space-between px-5">
          <div class="col aol-auto">
            <v-list-item-content>
              {{ date }}
            </v-list-item-content>
          </div>
          <div class="col aol-auto text-center">
            <v-list-item-content>
              <v-chip label outlined color="yellow" v-show="holiday === 'e'">
                予定外
              </v-chip>
              <v-btn
                label
                outlined
                color="red"
                v-show="holiday === '1'"
                @click="notifyBooking(date)"
              >
                休み
              </v-btn>
            </v-list-item-content>
          </div>
        </div>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script>
import { mapGetters } from 'vuex'
export default {
  props: ['name', 'daylist'],
  computed: {
    ...mapGetters(['isAuthenticated'])
  },
  methods: {
    notifyBooking (date) {
      if (this.isAuthenticated) {
        return this.$emit('booking', { date: date })
      }
      this.$parent.message = 'ログインしてください'
    }
  }
}
</script>
