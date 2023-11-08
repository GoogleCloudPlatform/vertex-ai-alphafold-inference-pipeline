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
/* eslint-disable react-refresh/only-export-components */

import { useState, createContext, useEffect } from "react";
import Snackbar from "@mui/material/Snackbar";
import { ResponsiveAppBar } from "./components/ResponsiveAppBar";
import { Alert, AlertColor, Box, Button, Drawer } from "@mui/material";
import { NewJob } from "./NewJob";
import JobResults from "./JobResults";
import axios from "axios";
const globalContext = createContext<{ accessToken: string | null }>({
  accessToken: null,
});

const BACKEND_HOST = import.meta.env.VITE_BACKEND_HOST ?? "";

function App() {
  const [showNotification, setShowNotification] = useState(false);
  const [notifContent, setNotifContent] = useState("");
  const [nofifType, setNotifType] = useState<AlertColor>("error");
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [clientId, setClientId] = useState("");
  const [jobsRefresh, setJobsRefresh] = useState(false);

  useEffect(() => {
    const fetchClientId = async () => {
      const response = await axios.get(`${BACKEND_HOST}/clientid`);
      setClientId(response.data);
    };
    fetchClientId();
  }, []);

  function showSnackbar(message: string, notificationType: AlertColor) {
    setNotifContent(message);
    setNotifType(notificationType);
    setShowNotification(true);
  }

  const handleCreateTestClick = () => {
    setDrawerOpen(true);
  };

  return (
    <>
      <globalContext.Provider value={{ accessToken: accessToken }}>
        <Snackbar
          open={showNotification}
          autoHideDuration={6000}
          anchorOrigin={{ vertical: "top", horizontal: "right" }}
          onClose={() => setShowNotification(false)}
        >
          <Alert
            onClose={() => {
              setShowNotification(false);
            }}
            severity={nofifType}
            sx={{ width: "100%" }}
          >
            {notifContent}
          </Alert>
        </Snackbar>
        <ResponsiveAppBar
          toolName={"AlphaFold Portal"}
          clientId={clientId}
          // onSignIn={(idToken: string, userInfo: string, accessToken: string) => {
          onSignIn={(accessToken: string) => {
            setAccessToken(accessToken);
          }}
          onError={(err: any) => showSnackbar(JSON.stringify(err), "error")}
        />
        <Box sx={{ margin: "20px" }}>
          <h2>Dashboard</h2>
          <JobResults refresh={jobsRefresh} />

          <Button
            variant="contained"
            sx={{ marginTop: "20px", justifyContent: "space-between" }}
            onClick={handleCreateTestClick}
          >
            <span>New Protein Folding</span>
          </Button>
          <Button
            variant="contained"
            sx={{
              marginTop: "20px",
              marginLeft: "15px",
              justifyContent: "space-between",
            }}
            onClick={() => location.reload()}
          >
            <span>Refresh</span>
          </Button>
          <Drawer
            anchor={"right"}
            open={drawerOpen}
            variant="persistent"
            onClose={() => setDrawerOpen(false)}
          >
            <NewJob
              createMode={true}
              onClose={(refresh: boolean) => {
                setDrawerOpen(false);
                if (refresh) {
                  setJobsRefresh(!jobsRefresh);
                  showSnackbar("Folding is in progress...", "success");
                }
                window.scrollTo(0, 0);
              }}
              onError={setShowNotification}
            />
          </Drawer>
        </Box>
      </globalContext.Provider>
    </>
  );
}

export { App, globalContext };
