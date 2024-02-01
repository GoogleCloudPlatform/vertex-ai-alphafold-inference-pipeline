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

/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/no-explicit-any */

import AppBar from "@mui/material/AppBar";
import Typography from "@mui/material/Typography";
import { GoogleSignInButton } from "./GoogleSignInButton";
import { checkAndExecuteFn } from "../common/CommonFunctions";

/**
 * ResponsiveAppBar functional component that displays navigation header
 * and a GoogleSignIn button if a clientId is provided
 *
 * @param {string=} [toolName=''] the Name to show next to Gtools in bar
 * @param {boolean=} [enableOneTap=true] enable/disable oneTap Sign In
 * @param {?string} clientId optional ClientId to use for Google Sign In
 * @param {?function} onSignIn optional Function to receive callback on successful signIn
 * @param {?function(Object)} onError optional function to receive error messages.
 * @return {JSX.Element}
 * @constructor
 */
function ResponsiveAppBar({
  toolName = "",
  enableOneTap = true,
  clientId,
  onSignIn,
  onError,
}: {
  toolName?: string;
  enableOneTap?: boolean;
  clientId?: string;
  onSignIn?: any;
  onError?: any;
}): JSX.Element {
  const handleSignIn = (
    idToken: any,
    userInformation: any,
    accessToken: any,
  ) => {
    checkAndExecuteFn(onSignIn, idToken, userInformation, accessToken);
  };
  return (
    <AppBar
      position="static"
      style={{
        display: "flex",
        flexDirection: "row",
        justifyContent: "space-between",
      }}
    >
      <Typography
        variant="h5"
        noWrap
        component="a"
        href="/"
        sx={{
          mr: 2,
          ml: 2,
          display: { xs: "none", md: "flex" },
          fontFamily: "Roboto Condensed",
          fontStyle: "italic",
          fontWeight: 700,
          letterSpacing: "0.01rem",
          color: "inherit",
          textDecoration: "none",
          alignItems: "center",
        }}
      >
        {toolName}
      </Typography>
      <span
        style={{
          display: "flex",
          flexDirection: "row",
          padding: "0.5rem 2rem",
          alignItems: "center",
        }}
      >
        {clientId && (
          <GoogleSignInButton
            clientId={clientId}
            enableOneTap={enableOneTap}
            onSignIn={handleSignIn}
            onError={onError}
          />
        )}
      </span>
    </AppBar>
  );
}
export { ResponsiveAppBar };
