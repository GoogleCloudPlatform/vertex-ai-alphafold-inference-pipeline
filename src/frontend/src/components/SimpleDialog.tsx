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

import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';
import { useEffect, createRef } from 'react';
import axios from 'axios';
import InfoIcon from '@mui/icons-material/Info';
import Tooltip from '@mui/material/Tooltip';

export interface SimpleDialogProps {
    open: boolean;
    selectedValue: string;
    onClose: (value: string) => void;
}

export default function SimpleDialog(props: SimpleDialogProps) {
    const { onClose, selectedValue, open } = props;
    const dialogRef = createRef<HTMLDivElement>();

    const handleClose = () => {
        onClose('');
    };

    useEffect(() => {
        if (selectedValue) {
            axios
                .get(`/protein?path=${encodeURIComponent(selectedValue)}`)
                .then((response) => {
                    const config = { backgroundColor: 'white' };
                    const viewer = window.$3Dmol?.createViewer(
                        dialogRef.current,
                        config
                    );
                    if (viewer) {
                        viewer.addModel(response.data, 'pdb'); /* load data */
                        viewer.setStyle(
                            {},
                            { stick: { color: 'spectrum' } }
                        ); /* style all atoms */
                        viewer.zoomTo(); /* set camera */
                        viewer.render(); /* render scene */
                        viewer.zoom(1.2, 1000); /* slight zoom */
                    }
                })
                .catch((error) => {
                    console.log('ERROR - geting PDB file', error);
                });
        }
    });

    return (
        <Dialog
            onClose={handleClose}
            open={open}
            fullWidth={true}
            maxWidth={'md'}>
            <DialogTitle>
                Protein Viewer
                <Tooltip style={{ marginLeft: '0.5rem' }} title='Protein viewer library by Koes, D., & Rego, N. 3Dmol.js: molecular visualization with WebGL [Computer software]. https://github.com/3dmol/3Dmol.js'>
                    <InfoIcon />
                </Tooltip>
            </DialogTitle>
            <div>
                <div
                    id='proteinViewer'
                    ref={dialogRef}
                    className='mol-container'
                    data-backgroundcolor='0xffffff'
                    style={{
                        marginLeft: 'auto',
                        marginRight: 'auto',
                        height: '800px',
                        width: '800px',
                        position: 'relative',
                    }}></div>
            </div>
        </Dialog>
    );
}
