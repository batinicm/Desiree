import axios from "axios"
import { defineStore } from "pinia";

export const useFastStore = defineStore('fast', {
    state: () => ({
        msg: '',
        songs: null
    }),
    actions: {
        async touchFast(){
            let {data} = await axios.get('');
            this.msg = data;
        },

        async getHomeSongs(){
            let {data} = await axios.get('homesong')
            this.songs = data
        }
    },
    persist: true
})