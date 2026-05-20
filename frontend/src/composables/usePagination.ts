import { ref, computed } from 'vue'

interface UsePaginationOptions {
  initialPage?: number
  initialPageSize?: number
  pageSizes?: number[]
}

export function usePagination(options: UsePaginationOptions = {}) {
  const {
    initialPage = 1,
    initialPageSize = 20,
    pageSizes = [10, 20, 50, 100]
  } = options

  const currentPage = ref(initialPage)
  const pageSize = ref(initialPageSize)
  const total = ref(0)

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  const offset = computed(() => (currentPage.value - 1) * pageSize.value)

  function setPage(page: number) {
    currentPage.value = page
  }

  function setPageSize(size: number) {
    pageSize.value = size
    currentPage.value = 1
  }

  function setTotal(count: number) {
    total.value = count
  }

  function reset() {
    currentPage.value = initialPage
    pageSize.value = initialPageSize
    total.value = 0
  }

  function paginateLocal<T>(data: T[]): T[] {
    const start = offset.value
    return data.slice(start, start + pageSize.value)
  }

  return {
    currentPage,
    pageSize,
    total,
    totalPages,
    offset,
    pageSizes,
    setPage,
    setPageSize,
    setTotal,
    reset,
    paginateLocal
  }
}
