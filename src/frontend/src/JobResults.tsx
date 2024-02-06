/*
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { useMemo, useState, useEffect, useContext } from 'react';
import {
    MaterialReactTable,
    useMaterialReactTable,
} from 'material-react-table';

import { globalContext } from './App';
import axios from 'axios';
import SimpleDialog from './components/SimpleDialog';

/* eslint-disable @typescript-eslint/no-explicit-any */
const BACKEND_HOST = import.meta.env.VITE_BACKEND_HOST ?? '';

export default function JobResults(props: any) {
    const [data, setData] = useState([]);
    const { accessToken } = useContext(globalContext);
    const [loading, setLoading] = useState(false);
    const [open, setOpen] = useState(false);
    const [selectedProteinPath, setSelectedProteinPath] = useState('');

    const handleClickOpen = (proteinPath: string) => {
        setOpen(true);
        setSelectedProteinPath(proteinPath);
    };

    const handleClose = (value: string) => {
        setOpen(false);
        setSelectedProteinPath(value);
    };

    useEffect(() => {
        if (accessToken) {
            const fetchJobs = async () => {
                const jobs = await axios.get(`${BACKEND_HOST}/status`, {
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                        'Content-Type': 'multipart/form-data',
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
                accessorKey: 'run_tag',
                header: 'Run Tag',
                muiTableHeadCellProps: { sx: { color: 'green' } },
                Cell: ({ cell }: { cell: any }) => (
                    <span>{cell.getValue()}</span>
                ),
            },
            {
                accessorFn: (row: { experiment_id: any }) =>
                    `${row.experiment_id}`,
                id: 'experiment_id',
                header: 'Experiment ID',
                muiTableHeadCellProps: { sx: { color: 'green' } },
                Cell: ({
                    renderedCellValue,
                    row,
                }: {
                    renderedCellValue: any;
                    row: any;
                }) => {
                    return (
                        <span>
                            <a
                                href={row.original.url_link}
                                target='_blank'
                                className='external-button'>
                                {renderedCellValue}
                            </a>
                        </span>
                    );
                },
            },
            {
                accessorKey: 'user',
                header: 'User',
                enableGrouping: false,
                muiTableHeadCellProps: { sx: { color: 'green' } },
                Cell: ({ cell }: { cell: any }) => (
                    <span>{cell.getValue()}</span>
                ),
            },
            {
                accessorKey: 'status',
                header: 'Status',
                enableGrouping: false,
                muiTableHeadCellProps: { sx: { color: 'green' } },
                Cell: ({ cell }: { cell: any }) => (
                    <span>{cell.getValue()}</span>
                ),
            },
            {
                accessorKey: 'duration',
                header: 'Duration',
                enableGrouping: false,
                muiTableHeadCellProps: { sx: { color: 'green' } },
                Cell: ({ cell }: { cell: any }) => (
                    <span>{cell.getValue()}</span>
                ),
            },
            {
                accessorKey: 'create_time',
                header: 'Created',
                enableGrouping: false,
                muiTableHeadCellProps: { sx: { color: 'green' } },
                Cell: ({ cell }: { cell: any }) => (
                    <span>{cell.getValue()}</span>
                ),
                sortingFn: (rowA: any, rowB: any, columnId: any) => {
                    return (
                        new Date(rowB.getValue(columnId)).getTime() -
                        new Date(rowA.getValue(columnId)).getTime()
                    );
                },
            },
            {
                accessorKey: 'sequence',
                header: 'Sequence',
                muiTableHeadCellProps: { sx: { color: 'green' } },
                Cell: ({ cell }: { cell: any }) => (
                    <span>{cell.getValue()}</span>
                ),
            },
            {
                accessorKey: 'ranking_confidence',
                header: 'Accuracy',
                enableGrouping: false,
                muiTableHeadCellProps: { sx: { color: 'green' } },
                Cell: ({ cell }: { cell: any }) => (
                    <span>{reformatDigit(cell.getValue())}</span>
                ),
            },
            {
                accessorKey: 'predict_uri',
                header: 'Predict URL',
                enableGrouping: false,
                muiTableHeadCellProps: { sx: { color: 'green' } },
                Cell: ({ row }: { row: any }) => (
                    <span>
                        {row.original.predict_uri === 'NA' ? (
                            'NA'
                        ) : (
                            <div>
                                <a
                                    href={row.original.predict_uri}
                                    target='_blank'
                                    className='external-button'>
                                    Open
                                </a>
                                &nbsp;&nbsp;
                                <a
                                    className='external-button'
                                    onClick={() => handleClickOpen(row.original.predict_uri + 'unrelaxed_protein.pdb')}>
                                    View
                                </a>
                            </div>
                        )}
                    </span>
                ),
            },
            {
                accessorKey: 'relax_uri',
                header: 'Relax URL',
                enableGrouping: false,
                muiTableHeadCellProps: { sx: { color: 'green' } },
                Cell: ({ row }: { row: any }) => (
                    <span>
                        {row.original.relax_uri === 'NA' ? (
                            'NA'
                        ) : (
                          <div>
                            <a
                                href={row.original.relax_uri}
                                target='_blank'
                                className='external-button'>
                                Open
                            </a>  &nbsp;&nbsp;
                                <a
                                    className='external-button'
                                    onClick={() => handleClickOpen(row.original.relax_uri + 'relaxed_protein.pdb')}>
                                    View
                                </a>
                            </div>
                        )}
                    </span>
                ),
            },
        ],
        []
    );

    //optionally, you can manage any/all of the table state yourself
    const [rowSelection, setRowSelection] = useState({});

    const reformatDigit = (value: any) => {
        return value != 'NA' ? value.toFixed(2) : 0;
    };

    useEffect(() => {
        //do something when the row selection changes
    }, [rowSelection]);

    const table = useMaterialReactTable({
        columns,
        data,
        enableGrouping: true,
        enableColumnDragging: false, //enable some features
        // enableRowSelection: true,
        enablePagination: false, //disable a default feature
        onRowSelectionChange: setRowSelection, //hoist internal state to your own state (optional)
        // state: { rowSelection,  }, //manage your own state, pass it back to the table (optional)
        state: { isLoading: loading },
        initialState: {
            grouping: ['run_tag', 'experiment_id', 'sequence'],
            density: 'compact',
            sorting: [
                { id: 'create_time', desc: true },
                { id: 'ranking_confidence', desc: true },
            ],
            columnVisibility: {
                create_time: false,
            },
        },
    });

    return (
        <>
            <MaterialReactTable table={table} />
            <SimpleDialog
                selectedValue={selectedProteinPath}
                onClose={handleClose}
                open={open}
            />
        </>
    );
}
