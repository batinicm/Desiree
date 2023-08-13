import axios from "axios"
import { defineStore } from "pinia";

export const useFastStore = defineStore('fast', {
    state: () => ({
        msg: ''
    }),
    actions: {
        async touchFast(){
            let {data} = await axios.get('');
            this.msg = data;
        }
    },
    persist: true
})