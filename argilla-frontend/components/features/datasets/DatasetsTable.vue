<template>
  <div class="container">
    <datasets-empty v-if="!datasets.length" />
    <div class="dataset__table" v-else>
      <div class="interactions">
        <base-search-bar
          @input="onSearch"
          :querySearch="querySearch"
          :placeholder="$t('searchDatasets')"
        />
      </div>
      <BaseTableInfo
        ref="table"
        :data="datasets"
        :columns="tableColumns"
        :row-link="datasetLink"
        :sorted-order="sortedOrder"
        :sorted-by-field="sortedByField"
        search-on="name"
        :query-search="querySearch"
        :empty-search-info="emptySearchInfo"
        :active-filters="activeFilters"
        @sort-column="onSortColumns"
        @onActionClicked="onActionClicked"
        @filter-applied="onColumnFilterApplied"
      />
    </div>
  </div>
</template>

<script>
import { useRoutes } from "@/v1/infrastructure/services";

export default {
  props: {
    datasets: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      querySearch: undefined,
      datasetLink: (dataset) => this.getDatasetLink(dataset),
      tableColumns: [
        {
          name: this.$t("datasetTable.name"),
          field: "name",
          class: "table-info__title",
          type: "main",
          component: {
            name: "DatasetQuestions",
            props: (item) => ({
              dataset: item,
            }),
          },
          actions: [
            {
              name: "copy-name",
              icon: "copy",
              title: "Copy name to clipboard",
              tooltip: "Copied",
            },
            {
              name: "copy-url",
              icon: "link",
              title: "Copy url to clipboard",
              tooltip: "Copied",
            },
            {
              name: "go-to-settings",
              icon: "settings",
              title: "Go to dataset settings",
              tooltip: "Dataset settings",
            },
          ],
        },
        {
          name: this.$t("datasetTable.workspace"),
          field: "workspace",
          class: "text",
          type: "text",
          filtrable: "true",
        },
        {
          name: this.$t("datasetTable.createdAt"),
          field: "createdAt",
          class: "date",
          type: "date",
          sortable: "true",
        },
        {
          name: this.$t("datasetTable.lastActivityAt"),
          field: "lastActivityAt",
          class: "date",
          type: "date",
          sortable: "true",
        },
        {
          name: this.$t("datasetTable.progress"),
          class: "progress",
          component: {
            name: "DatasetProgress",
            props: (item) => ({
              datasetId: item.id,
            }),
          },
        },
      ],
      emptySearchInfo: {
        title: "0 datasets found",
      },
      externalLinks: [],
      sortedOrder: "desc",
      sortedByField: "updatedAt",
    };
  },
  computed: {
    activeFilters() {
      const workspaces = this.workspaces;
      return [{ column: "workspace", values: workspaces }];
    },
    workspaces() {
      return this.$route.query.workspaces?.split(",") ?? [];
    },
  },
  methods: {
    clearFilters() {
      if (this.$refs.table) {
        this.activeFilters.forEach((filter) => {
          this.$refs.table.onApplyFilters({ field: filter.column }, []);
        });

        this.querySearch = undefined;
      }
    },
    onSearch(event) {
      this.querySearch = event;
    },
    onSortColumns(by, order) {
      this.sortedByField = by;
      this.sortedOrder = order;
    },
    onColumnFilterApplied({ column, values }) {
      const updateUrlParamsFor = (
        values,
        paramKey,
        currentParams,
        valuesToPush
      ) => {
        if (values === currentParams) return;

        const query = createQueryFor(values, paramKey, valuesToPush);
        this.$router.push({ query });
      };

      const createQueryFor = (values, paramKey, valuesToPush) => {
        if (values.length) {
          return { ...this.$route.query, [paramKey]: valuesToPush };
        }

        const { [paramKey]: keyToEscape, ...rest } = this.$route.query;
        return { ...rest };
      };

      switch (column) {
        case "workspace":
          updateUrlParamsFor(
            values,
            "workspaces",
            this.workspaces,
            values.join(",")
          );
          break;
      }
    },
    onActionClicked(action, dataset) {
      switch (action) {
        case "go-to-settings":
          this.goToSetting(dataset);
          break;
        case "copy-url":
          this.copyUrl(dataset);
          break;
        case "copy-name":
          this.copyName(dataset);
          break;
        default:
          console.warn(action);
      }
    },
    copy(value) {
      this.$copyToClipboard(value);
    },
    copyUrl(dataset) {
      this.copy(`${window.origin}${this.getDatasetLink(dataset)}`);
    },
    copyName({ name }) {
      this.copy(name);
    },
  },
  setup() {
    return useRoutes();
  },
};
</script>

<style lang="scss" scoped>
.container {
  display: flex;
  justify-content: center;
  padding: 0 4em;
  @include media("<=tablet") {
    padding: 0 $base-space * 2;
  }
}
.dataset {
  &__table {
    width: 100%;
    max-width: 1500px;
    padding: 0 $base-space * 6;
    display: flex;
    flex-direction: column;
    @include media("<=tablet") {
      padding: 0;
    }
  }
}
.interactions {
  display: flex;
  align-items: flex-end;
  margin: 2em 0 1em 0;
}

.search-area {
  width: clamp(300px, 30vw, 800px);
}

:deep(.table-info__item__col:nth-last-of-type(-n + 4)) {
  @include media("<desktop") {
    display: none;
  }
}
</style>
