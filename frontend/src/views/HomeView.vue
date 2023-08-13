<script setup>
import HomeCard from '../components/HomeCard.vue';
import { useFastStore } from '../stores/fast'
import { storeToRefs } from 'pinia'

const useFast = useFastStore()
const {playlists} = storeToRefs(useFast)

useFast.getHomePlaylists()

</script>

<template>
    <div class="p-8" v-for="playlist in playlists" :key="playlist">
        <div class="playlist-title"> {{playlist.Title}} </div>
        <div class="text-white text-l"> {{playlist.Description}} </div>
        <div class="grid-container">
            <div class="grid-item" v-for="track in playlist.Songs" :key="track">
                <HomeCard :track="track" />
            </div>
        </div>
    </div>
</template>

<style>
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.grid-item {
  border-radius: 4px;
}

.playlist-title {
  color: white;
  font-size: 1.5em;
  font-family: "Avenir Next Heavy" !important;
}
</style>