import axios from "axios"
import { defineStore } from "pinia";

export const useFastStore = defineStore('fast', {
    state: () => ({
        songs: null,
        playlists: null
    }),
    actions: {
        async getHomeSongs(){
            let {data} = await axios.get('homesong')
            this.songs = data
        },

        async getHomePlaylists(){
            let {data} = await axios.get('topplaylists')
            this.playlists = data
        }
    },
    persist: true
})