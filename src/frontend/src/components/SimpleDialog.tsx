import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';
import { useEffect, createRef } from 'react';
import axios from 'axios';

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
            <DialogTitle>Protein Viewer</DialogTitle>
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
