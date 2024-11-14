<template>
    <div>
        <header class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-2.5">
            <Breadcrumbs class="h-7" :items="[{ label: 'All Tasks', route: { name: 'CedAll' } }]" />
            <div class="flex">
                <!-- Status Filter -->
                <Select class="w-36 pl-7 pr-7 mr-4" v-model="filters.status" :options="statusOptions"
                    placeholder="Filter by Status">
                    <template #prefix>
                        <LucideFilter class="w-4 text-gray-600" />
                    </template>
                </Select>
                <!-- People Filter -->
                <Select class="w-44 pl-7 pr-7 mr-4" v-model="filters.assignee" :options="peopleOptions"
                    placeholder="Filter by Assignee">
                    <template #prefix>
                        <LucideUser class="w-4 text-gray-600" />
                    </template>
                </Select>
                <Select class="w-44 pl-7 pr-7 mr-4" v-model="orderBy" :options="orderOptions">
                    <template #prefix>
                        <LucideArrowDownUp class="w-4 text-gray-600" />
                    </template>
                </Select>
                <Button variant="solid" @click="showNewTaskDialog">
                    <template #prefix>
                        <LucidePlus class="h-4 w-4" />
                    </template>
                    Add new
                </Button>
            </div>

        </header>

        <div class="mx-auto w-full max-w-4xl px-5">
            <div class="py-6">
                <TaskList :listOptions="listOptions" :groupByStatus="false" />
                <NewTaskDialog ref="newTaskDialog" />
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, computed, watch } from 'vue'
import { getCachedListResource, usePageMeta, Breadcrumbs, Select, call } from 'frappe-ui'
import { getUser } from '@/data/users'

let newTaskDialog = ref(null)

// State Variables
const orderBy = ref('creation desc')
const filters = ref({
    status: '', // Status filter
    assignee: '', // Assignee filter
}) // Filters can be expanded for additional criteria

// Sorting Options
const orderOptions = [
    { label: 'Creation Date ASC', value: 'creation asc' },
    { label: 'Creation Date DESC', value: 'creation desc' },
    { label: 'Title ASC', value: 'title asc' },
    { label: 'Title DESC', value: 'title desc' }
]


// Status Filter Options
const statusOptions = [
    { label: 'All', value: '' },
    { label: 'Open', value: 'Open' },
    { label: 'In Progress', value: 'In Progress' },
    { label: 'Closed', value: 'Closed' }
]

// People Filter Options (Dynamic Loading)
const peopleOptions = ref([])


// Load Assignees for the People Filter
async function loadPeopleOptions() {
    const response = await call({
        method: 'gameplan.extends.client.get_list', // Adjust the API method based on your backend
    })
    if (response.message) {
        peopleOptions.value = [{ label: 'All', value: '' }].concat(
            response.message.map(user => ({
                label: user.full_name || user.name,
                value: user.name,
            }))
        )
    }
}

let listOptions = computed(() => ({
    filters: {
        status: filters.value.status,
        assigned_to: filters.value.assignee,
    },
    pageLength: 999,
    orderBy: orderBy.value
}))

function showNewTaskDialog() {
    newTaskDialog.value.show({
        defaults: {
            assigned_to: getUser('sessionUser').name,
        },
        onSuccess: () => {
            let tasks = getCachedListResource(['Tasks', listOptions.value])
            if (tasks) {
                tasks.reload()
            }
        },
    })
}

usePageMeta(() => {
    return {
        title: 'All Tasks',
        emoji: '👨‍👩‍👧‍👦',
    }
})

// Watch for Sorting Changes and Reload Tasks
watch([orderBy, filters], () => {
    const tasks = getCachedListResource(['Tasks', listOptions.value])
    if (tasks) {
        tasks.reload()
    }
})
// Initialize People Options
loadPeopleOptions()
</script>