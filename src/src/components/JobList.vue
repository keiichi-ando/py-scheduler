<template>
  <v-card class="justify-space-between px-5" dark>
    <v-card-title class="subheadign font-weight-bold"> scheduled </v-card-title>
    <v-divider></v-divider>
    <v-data-table :headers="headers" :items="joblist"></v-data-table>
  </v-card>
</template>

<script>
export default {
  props: ['joblist'],
  data () {
    return {
      headers: [
        {
          text: 'id',
          value: 'id'
        },
        {
          text: 'func',
          value: 'func'
        },
        {
          text: 'args',
          value: 'args'
        },
        {
          text: 'next_run_at',
          value: 'next_run_at'
        },
        {
          text: 'trigger',
          value: 'trigger'
        }
      ]
    }
  }
}
</script>
