/*
 * Copyright 2023 Google LLC
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

/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-unused-vars */

import {
  Alert,
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Snackbar,
  AlertColor,
  TextField,
  Typography,
  Backdrop,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from "@mui/material";
import axios from "axios";
import { useState, useContext, useEffect } from "react";
import { globalContext } from "./App";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { calculateAcceleratorCount } from "./common/CommonFunctions";

// import { useLocation } from 'react-router-dom';

function NewJob({ onClose }: { createMode: any; onClose: any; onError: any }) {
  const errorSeverity: AlertColor = "error";
  const successSeverity: AlertColor = "success";

  const [fileName, setFileName] = useState<string | null>(null);
  const [fastaCheckResult, setFastaCheckResult] = useState<string | null>(null);
  const [file, setFile] = useState<any>(null);
  const [experimentId, setExperimentId] = useState("");
  const [runTag, setRunTag] = useState("");
  const [smallBFD, setSmallBFD] = useState("yes");
  const [proteinType, setProteinType] = useState("");
  const [relaxation, setRelaxation] = useState("no");
  const [predictionCount, setPredictionCount] = useState("3");
  const [predictMachineType, setPredictMachineType] = useState("g2-standard-8");
  const [relaxMachineType, setRelaxMachineType] = useState("g2-standard-8");

  const [snackbarContent, setSnackbarContent] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] =
    useState<AlertColor>(errorSeverity);
  const [open, setOpen] = useState(true);
  const [loading, setLoading] = useState(false);

  const { accessToken } = useContext(globalContext);
  const BACKEND_HOST = import.meta.env.VITE_BACKEND_HOST ?? "";

  const handleFoldRun = () => {
    if (!accessToken) {
      setSnackbarContent("AccessToken is missing. Please login first.");
      setOpen(true);
      return;
    }
    setLoading(true);
    if (!file) {
      setSnackbarContent(`FASTA file is missing. Please Upload a FASTA file.`);
      setOpen(true);
      setLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append("runTag", runTag);
    formData.append("experimentId", experimentId);
    formData.append("smallBFD", smallBFD);
    formData.append("relaxation", relaxation);
    formData.append("proteinType", proteinType);
    formData.append("predictionCount", predictionCount);

    formData.append("predictMachineType", predictMachineType);
    formData.append(
      "acceleratorCount",
      calculateAcceleratorCount(predictMachineType),
    );

    formData.append("relaxMachineType", relaxMachineType);
    formData.append(
      "relaxAcceleratorCount",
      calculateAcceleratorCount(relaxMachineType),
    );

    formData.append("file", file);

    return axios
      .post(`${BACKEND_HOST}/fold`, formData, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "multipart/form-data",
        },
      })
      .then((res) => {
        setSnackbarContent(res.data);
        setSnackbarSeverity(successSeverity);
        setOpen(true);
        setLoading(false);
        onClose(true); // success and need to refresh jobs result
      })
      .catch((error) => {
        setSnackbarContent(error);
        setSnackbarSeverity(errorSeverity);
        setOpen(true);
        setLoading(false);
      });
  };

  const handleCheckFasta = () => {
    if (!accessToken) {
      setSnackbarContent("AccessToken is missing. Please login first.");
      setOpen(true);
      return;
    }
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    return axios
      .post(`${BACKEND_HOST}/check-fasta`, formData, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "multipart/form-data",
        },
      })
      .then((res) => {
        const protein = res.data.isMonomer ? "monomer" : "multimer";
        setProteinType(protein);
        setFastaCheckResult(
          ` Protein Type: ${protein}. Residue: ${res.data.residue}`,
        );
        setLoading(false);
      })
      .catch((error) => {
        setSnackbarContent(error);
        setSnackbarSeverity(errorSeverity);
        setOpen(true);
        setLoading(false);
      });
  };

  useEffect(() => {
    if (file) {
      handleCheckFasta();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [file]);

  const handleCancelJob = () => {
    onClose(false);
  };
  const handleChange = (event: any, callback: any) => {
    callback(event.target.value);
  };

  const LoadingBackdrop = (
    <Backdrop
      sx={{ color: "#fff", zIndex: (theme) => theme.zIndex.drawer + 1 }}
      open={loading}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <CircularProgress color="inherit" />
        <span style={{ marginTop: 5 }}>Loading...</span>
      </div>
    </Backdrop>
  );

  return (
    <>
      {LoadingBackdrop}
      {snackbarContent && (
        <Snackbar
          anchorOrigin={{ vertical: "top", horizontal: "right" }}
          open={open}
          onClose={() => {
            setOpen(false);
          }}
          autoHideDuration={6000}
          key={"top" + "left"}
        >
          <Alert
            onClose={() => {
              setOpen(false);
            }}
            severity={snackbarSeverity}
            sx={{ width: "100%" }}
          >
            {snackbarContent}
          </Alert>
        </Snackbar>
      )}

      <Box
        sx={{ margin: "1rem" }}
        style={{ display: "flex", flexDirection: "column" }}
      >
        <h2>Select the protein FASTA file to determine structure</h2>
        <Typography style={{ display: "flex", flexDirection: "row" }}>
          <Button variant="contained" component="label" disabled={false}>
            Upload FASTA
            <input
              type="file"
              hidden
              id="file-uploader-input"
              onChange={(event) => {
                const file: any = (event.target as HTMLInputElement)
                  ?.files?.[0];
                const reader = new FileReader();
                reader.onload = () => {
                  setFile(file);
                  setFileName(file.name);
                  handleCheckFasta();
                };
                if (file) {
                  reader.readAsText(file);
                }
              }}
              accept=".fasta"
            ></input>
          </Button>
        </Typography>

        <div style={{ display: "flex", margin: "5px" }}>
          {fileName ? (
            <div>
              {fileName}
              <span
                style={{ marginLeft: "5px", verticalAlign: "top" }}
                className="google-symbols"
              >
                check_circle
              </span>
              <span>{fastaCheckResult}</span>
            </div>
          ) : (
            "No file chosen."
          )}
        </div>
        <span style={{ width: "90%" }}>
          <TextField
            onBlur={(e) => handleChange(e, setRunTag)}
            required={true}
            label="Run Tag"
            variant="outlined"
            sx={{ width: "100%", mt: 2 }}
            size="small"
            helperText="This is used to group multiple experiment 
              ID under the same group. Ex: group-amylase"
          />
        </span>
        <span style={{ width: "90%" }}>
          <TextField
            onBlur={(e) => handleChange(e, setExperimentId)}
            required={true}
            label="Experiment ID"
            variant="outlined"
            sx={{ width: "100%", mt: 2 }}
            size="small"
            helperText="Ex: amylase-fold-12"
          />
        </span>

        <span style={{ width: "90%", marginTop: "25px" }}>
          <Accordion sx={{ width: "482px" }}>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              aria-controls="panel1a-content"
              id="panel1a-header"
            >
              <Typography>Advanced Settings</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <FormControl sx={{ mt: 2, minWidth: "100%" }} size="small">
                <InputLabel id="protein-type-select-label">
                  Protein Type
                </InputLabel>
                <Select
                  labelId="protein-type-select-label"
                  required={true}
                  id="proteinType"
                  value={proteinType}
                  label="Protein Type"
                  size="small"
                  onChange={(e) => handleChange(e, setProteinType)}
                >
                  <MenuItem value={"monomer"}>Monomer</MenuItem>
                  <MenuItem value={"multimer"}>Multimer</MenuItem>
                </Select>
              </FormControl>
              <FormControl sx={{ mt: 2, minWidth: "100%" }} size="small">
                <InputLabel id="small-bfd-select-label">
                  Use Small BFD
                </InputLabel>
                <Select
                  labelId="small-bfd-select-label"
                  required={true}
                  id="useSmallBfd"
                  value={smallBFD}
                  label="Use Small BFD"
                  size="small"
                  onChange={(e: any) => handleChange(e, setSmallBFD)}
                >
                  <MenuItem value={"yes"}>Yes</MenuItem>
                  <MenuItem value={"no"}>No</MenuItem>
                </Select>
              </FormControl>
              <TextField
                required={true}
                onBlur={(e) => handleChange(e, setPredictionCount)}
                label="Multimer Predictions per model (#)"
                sx={{ width: "100%", mt: 2 }}
                size="small"
                value={predictionCount}
                variant="outlined"
                helperText="Sample numbers: 3, 4, 5, 6. Ex: 3"
              />
              <FormControl sx={{ mt: 2, minWidth: "100%" }} size="small">
                <InputLabel id="relaxation-select-label">
                  Run relaxation after folding
                </InputLabel>
                <Select
                  labelId="relaxation-select-label"
                  required={true}
                  id="relaxation"
                  value={relaxation}
                  label="Run relaxation after folding"
                  size="small"
                  onChange={(e) => handleChange(e, setRelaxation)}
                >
                  <MenuItem value={"yes"}>Yes</MenuItem>
                  <MenuItem value={"no"}>No</MenuItem>
                </Select>
              </FormControl>
              <FormControl sx={{ mt: 2, minWidth: "100%" }} size="small">
                <InputLabel id="predict-machine-type-select-label">
                  Prediction Machine Type
                </InputLabel>
                <Select
                  labelId="predict-machine-type-select-label"
                  id="prediction"
                  required={true}
                  value={predictMachineType}
                  label="Run relaxation after folding"
                  size="small"
                  onChange={(e) => handleChange(e, setPredictMachineType)}
                >
                  <MenuItem value={"g2-standard-8"}>
                    g2-standard-8 (L4)
                  </MenuItem>
                  <MenuItem value={"g2-standard-16"}>
                    g2-standard-16 (L4)
                  </MenuItem>
                  <MenuItem value={"g2-standard-32"}>
                    g2-standard-32 (L4)
                  </MenuItem>
                  <MenuItem value={"g2-standard-48"}>
                    g2-standard-48 (L4)
                  </MenuItem>
                  <MenuItem value={"a2-highgpu-1g"}>
                    a2-highgpu-1g (A100)
                  </MenuItem>
                  <MenuItem value={"a2-highgpu-2g"}>
                    a2-highgpu-2g (A100)
                  </MenuItem>
                  <MenuItem value={"a2-highgpu-4g"}>
                    a2-highgpu-4g (A100)
                  </MenuItem>
                  <MenuItem value={"a2-highgpu-8g"}>
                    a2-highgpu-8g (A100)
                  </MenuItem>
                  <MenuItem value={"a2-megagpu-16g"}>
                    a2-highgpu-16g (A100)
                  </MenuItem>
                </Select>
              </FormControl>

              <FormControl sx={{ mt: 2, minWidth: "100%" }} size="small">
                <InputLabel id="relax-machine-type-select-label">
                  Relaxation Machine Type
                </InputLabel>
                <Select
                  labelId="relax-machine-type-select-label"
                  id="relaxation"
                  required={true}
                  value={relaxMachineType}
                  label="Run relaxation after folding"
                  size="small"
                  onChange={(e) => handleChange(e, setRelaxMachineType)}
                >
                  <MenuItem value={"g2-standard-8"}>
                    g2-standard-8 (L4)
                  </MenuItem>
                  <MenuItem value={"g2-standard-16"}>
                    g2-standard-16 (L4)
                  </MenuItem>
                  <MenuItem value={"g2-standard-32"}>
                    g2-standard-32 (L4)
                  </MenuItem>
                  <MenuItem value={"g2-standard-48"}>
                    g2-standard-48 (L4)
                  </MenuItem>
                  <MenuItem value={"a2-highgpu-1g"}>
                    a2-highgpu-1g (A100)
                  </MenuItem>
                  <MenuItem value={"a2-highgpu-2g"}>
                    a2-highgpu-2g (A100)
                  </MenuItem>
                  <MenuItem value={"a2-highgpu-4g"}>
                    a2-highgpu-4g (A100)
                  </MenuItem>
                  <MenuItem value={"a2-highgpu-8g"}>
                    a2-highgpu-8g (A100)
                  </MenuItem>
                  <MenuItem value={"a2-megagpu-16g"}>
                    a2-highgpu-16g (A100)
                  </MenuItem>
                </Select>
              </FormControl>
            </AccordionDetails>
          </Accordion>
        </span>
        <div style={{ display: "flex", flexDirection: "row" }}>
          <Button
            variant="contained"
            sx={{ marginTop: "20px", width: "200px", marginRight: "5px" }}
            onClick={handleFoldRun}
          >
            <span>Run AlphaFold</span>
          </Button>
          <Button
            variant="contained"
            sx={{ marginTop: "20px", width: "100px" }}
            onClick={handleCancelJob}
          >
            <span>Close</span>
          </Button>
        </div>
      </Box>
    </>
  );
}

export { NewJob };
