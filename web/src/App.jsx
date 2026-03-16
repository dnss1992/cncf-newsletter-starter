import React from 'react';
import { AppBar, Toolbar, Typography, Container, Box, Link } from '@mui/material';
import { Routes, Route, Link as RouterLink } from 'react-router-dom';
import Home from './Home';
import About from './About';

function App() {
  return (
    <Box display="flex" flexDirection="column" minHeight="100vh">
      <AppBar position="static">
        <Toolbar>
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            color="inherit"
            sx={{ textDecoration: 'none' }}
          >
            CNCF News
          </Typography>
          <Box flexGrow={1} />
          <Link component={RouterLink} to="/about" color="inherit" underline="none">
            About
          </Link>
        </Toolbar>
      </AppBar>
      <Container sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </Container>
      <Box component="footer" textAlign="center" py={2}>
        <Typography variant="body2">© {new Date().getFullYear()} CNCF News</Typography>
      </Box>
    </Box>
  );
}

export default App;
