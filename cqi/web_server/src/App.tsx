import './App.css'

import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core';
import PageContainer from "./PageContainer.tsx";

function App() {
    return <MantineProvider>
        <PageContainer/>
    </MantineProvider>;
}

export default App
