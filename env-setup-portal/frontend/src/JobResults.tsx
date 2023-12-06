import { useMemo, useState, useEffect, useContext } from "react";
import {
  MaterialReactTable,
  useMaterialReactTable,
} from "material-react-table";

import { globalContext } from "./App";
import axios from "axios";
/* eslint-disable @typescript-eslint/no-explicit-any */
const BACKEND_HOST = import.meta.env.VITE_BACKEND_HOST ?? "";

export default function JobResults(props: any) {
  const [data, setData] = useState([]);
  const { accessToken } = useContext(globalContext);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (accessToken) {
      const fetchJobs = async () => {
        const jobs = await axios.get(`${BACKEND_HOST}/status`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "multipart/form-data",
          },
        });
        setData(jobs.data);
        setLoading(false);
      };
      setLoading(true);
      fetchJobs();
    }
  }, [accessToken, props.refresh]);

  const columns = useMemo(
    () => [
      {
        accessorKey: "run_tag",
        header: "Run Tag",
        muiTableHeadCellProps: { sx: { color: "green" } },
        Cell: ({ cell }: { cell: any }) => <span>{cell.getValue()}</span>,
      },
      {
        accessorFn: (row: { experiment_id: any }) => `${row.experiment_id}`,
        id: "experiment_id",
        header: "Experiment ID",
        enableGrouping: false,
        muiTableHeadCellProps: { sx: { color: "green" } },
        Cell: ({
          renderedCellValue,
          row,
        }: {
          renderedCellValue: any;
          row: any;
        }) => {
          console.log("WOR", row.original.url_link);
          return (
            <span>
              <a
                href={row.original.url_link}
                target="_blank"
                className="external-button"
              >
                {renderedCellValue}
              </a>
            </span>
          );
        },
      },
      {
        accessorKey: "user",
        header: "User",
        muiTableHeadCellProps: { sx: { color: "green" } },
        Cell: ({ cell }: { cell: any }) => <span>{cell.getValue()}</span>,
      },
      {
        accessorKey: "status",
        header: "Status",
        muiTableHeadCellProps: { sx: { color: "green" } },
        Cell: ({ cell }: { cell: any }) => <span>{cell.getValue()}</span>,
      },
      {
        accessorKey: "duration",
        header: "Duration",
        enableGrouping: false,
        muiTableHeadCellProps: { sx: { color: "green" } },
        Cell: ({ cell }: { cell: any }) => <span>{cell.getValue()}</span>,
      },
      {
        accessorKey: "sequence",
        header: "Sequence",
        enableGrouping: false,
        muiTableHeadCellProps: { sx: { color: "green" } },
        Cell: ({ cell }: { cell: any }) => <span>{cell.getValue()}</span>,
      },
      {
        accessorKey: "top_predict_uri",
        header: "TOP Predict URL",
        enableGrouping: false,
        muiTableHeadCellProps: { sx: { color: "green" } },
        Cell: ({ row }: { row: any }) => (
          <span>
            {row.original.top_predict_uri === "NA" ? (
              "NA"
            ) : (
              <a
                href={row.original.top_relax_uri}
                target="_blank"
                className="external-button"
              >
                Open
              </a>
            )}
          </span>
        ),
      },
      {
        accessorKey: "top_relax_uri",
        header: "Top Relax URL",
        enableGrouping: false,
        muiTableHeadCellProps: { sx: { color: "green" } },
        Cell: ({ row }: { row: any }) => (
          <span>
            {row.original.top_relax_uri === "NA" ? (
              "NA"
            ) : (
              <a
                href={row.original.top_relax_uri}
                target="_blank"
                className="external-button"
              >
                Open
              </a>
            )}
          </span>
        ),
      },
    ],
    [],
  );

  //optionally, you can manage any/all of the table state yourself
  const [rowSelection, setRowSelection] = useState({});

  useEffect(() => {
    //do something when the row selection changes
  }, [rowSelection]);

  const table = useMaterialReactTable({
    columns,
    data,
    enableGrouping: true,
    enableColumnOrdering: true, //enable some features
    // enableRowSelection: true,
    enablePagination: false, //disable a default feature
    onRowSelectionChange: setRowSelection, //hoist internal state to your own state (optional)
    // state: { rowSelection,  }, //manage your own state, pass it back to the table (optional)
    state: { isLoading: loading },
    initialState: { grouping: ["run_tag"] },
  });

  return (
    <MaterialReactTable table={table} /> //other more lightweight MRT sub components also available
  );
}
