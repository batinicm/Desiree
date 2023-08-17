<script setup>
import { toRefs } from 'vue'
import { RouterLink } from 'vue-router';

import { useSongStore } from '../stores/song'
import { storeToRefs } from 'pinia';
const useSong = useSongStore()

const props = defineProps({
    track: Object
})
const { track } = toRefs(props)
</script>

<template>
    <RouterLink to="library">
        <div @click="useSong.loadMasterSong(track)" class="bg-[#111111] p-4 rounded-md m-2 hover:bg-[#252525] cursor-pointer">
            <img class="rounded-md" width="300" height="300" :src="track.ImageHref" alt="">
            <div class="text-white pt-4 font-semibold text-[17px]">{{ track.Name }}</div>
            <div class="text-gray-400 pt-1 pb-3 text-[14px]">{{ track.Artist }}</div>
        </div>
    </RouterLink>
</template>
