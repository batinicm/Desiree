import axios from "axios"
import { defineStore } from "pinia";

export const useFastStore = defineStore('fast', {
    state: () => ({
        playlists: null
    }),
    actions: {

        async getHomePlaylists(){
            let {data} = await axios.get('topplaylists')
            this.playlists = data
        }
    },
    persist: true
})