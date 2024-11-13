<template>
    <div>
        <header class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-2.5">
            <Breadcrumbs class="h-7" :items="[{ label: 'All Tasks', route: { name: 'CedAll' } }]" />
            <div class="flex">
                <Select class="w-44 pl-7 pr-7 mr-4" :options="[
                    { label: 'Creation Date ASC', value: 'creation asc' },
                    { label: 'Creation Date DESC', value: 'creation desc' }
                ]" v-model="orderBy">
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
import { ref, computed } from 'vue'
import { getCachedListResource, usePageMeta, Breadcrumbs } from 'frappe-ui'
import { getUser } from '@/data/users'

let newTaskDialog = ref(null)

let listOptions = computed(() => ({
    filters: {},
    pageLength: 999,
    orderBy: 'creation desc'
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
</script>