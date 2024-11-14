<template>
    <div>
        <header class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-2.5">
            <Breadcrumbs class="h-7" :items="[{ label: 'All Tasks', route: { name: 'CedAll' } }]" />
            <div class="flex">
                <!-- Status Filter -->
                <Select class="w-36 pl-7 pr-7 mr-4" v-model="filters.status" :options="statusOptions">
                    <template #prefix>
                        <LucideFilter class="w-4 text-gray-600" />
                    </template>
                </Select>
                <!-- People Filter -->
                <Select class="w-44 pl-7 pr-7 mr-4" v-model="filters.assignee" :options="peopleOptions"
                    :key="peopleOptions.length">
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
    { label: 'Backlog', value: 'Backlog' },
    { label: 'Todo', value: 'Todo' },
    { label: 'In Progress', value: 'In Progress' },
    { label: 'Done', value: 'Done' },
    { label: 'Canceled', value: 'Canceled' }
]

// People Filter Options (Dynamic Loading)
const peopleOptions = ref([])


// Load Assignees for the People Filter
async function loadPeopleOptions() {
    try {
        const response = await call('gameplan.api.get_user_info', { data: {} });
        if (response.length > 0) {
            peopleOptions.value = [{ label: 'All', value: '' }, ...response.map(user => ({
                label: user.full_name || user.name,
                value: user.name,
            }))];
            // Manually trigger dropdown component update
            filters.value.assignee = ''; // Reset the dropdown to trigger a UI update
        }
    } catch (error) {
        console.error("Failed to load people options:", error);
    }
}

let listOptions = computed(() => {
    const appliedFilters = {}

    // Only add status filter if it has a valid value
    if (filters.value.status && filters.value.status !== 'all') {
        appliedFilters.status = filters.value.status
    }

    // Only add assigned_to filter if it has a valid value
    if (filters.value.assignee && filters.value.assignee !== 'all') {
        appliedFilters.assigned_to = filters.value.assignee
    }

    return {
        filters: appliedFilters,
        pageLength: 999,
        orderBy: orderBy.value,
    }
})


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

// Watch peopleOptions to ensure it triggers a re-render
watch(peopleOptions, (newOptions) => {
    if (newOptions.length > 0) {
        console.log("People options updated:", newOptions)
    }
})
// Initialize People Options
loadPeopleOptions()
</script>