import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import { globalContext } from "./App";
import axios from "axios";
import { useEffect, useState, useContext } from "react";
/* eslint-disable @typescript-eslint/no-explicit-any */
const BACKEND_HOST = import.meta.env.VITE_BACKEND_HOST ?? "";

export default function JobResults(props: any) {
  const [rows, setRows] = useState([]);
  const { accessToken } = useContext(globalContext);

  useEffect(() => {
    const fetchJobs = async () => {
      const jobs = await axios.get(`${BACKEND_HOST}/status`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "multipart/form-data",
        },
      });
      setRows(jobs.data);
    };
    fetchJobs();
  }, [accessToken, props.refresh]);

  return (
    <TableContainer component={Paper}>
      <Table sx={{ minWidth: 650 }} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell align="left">Experiment ID</TableCell>
            <TableCell align="left">User</TableCell>
            <TableCell align="right">Sequence</TableCell>
            <TableCell align="right">Status</TableCell>
            <TableCell align="right">Duration</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row: any) => (
            <TableRow
              key={row.experiment_id}
              sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
            >
              <TableCell component="th" scope="row">
                <a href={row.url_link} target="_blank">
                  {row.experiment_id}
                </a>
                &nbsp;|&nbsp;
                <a href={row.url_all_structures} target="_blank">
                  all candidates structures
                </a>
              </TableCell>
              <TableCell align="left">{row.user}</TableCell>
              <TableCell align="right">{row.sequence}</TableCell>
              <TableCell align="right">{row.status}</TableCell>
              <TableCell align="right">{row.duration}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
