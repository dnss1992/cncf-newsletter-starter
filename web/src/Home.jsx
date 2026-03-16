import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Typography,
  TextField,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
} from '@mui/material';

function summarize(text) {
  return text.split(/\s+/).slice(0, 30).join(' ');
}

function Home() {
  const [items, setItems] = useState([]);
  const [project, setProject] = useState('');
  const [type, setType] = useState('');
  const [search, setSearch] = useState('');
  const [summary, setSummary] = useState('');

  useEffect(() => {
    fetch('items.json')
      .then((r) => r.json())
      .then((data) => setItems(data));
  }, []);

  const projects = Array.from(new Set(items.map((i) => i.project)));
  const types = Array.from(new Set(items.map((i) => i.type)));

  const filtered = items.filter((it) => {
    return (
      (!project || it.project === project) &&
      (!type || it.type === type) &&
      (!search || it.title.toLowerCase().includes(search.toLowerCase()))
    );
  });

  return (
    <Box>
      <Box display="flex" gap={2} mb={2}>
        <TextField
          select
          label="Project"
          value={project}
          onChange={(e) => setProject(e.target.value)}
          sx={{ minWidth: 120 }}
        >
          <MenuItem value="">All</MenuItem>
          {projects.map((p) => (
            <MenuItem key={p} value={p}>
              {p}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          select
          label="Type"
          value={type}
          onChange={(e) => setType(e.target.value)}
          sx={{ minWidth: 120 }}
        >
          <MenuItem value="">All</MenuItem>
          {types.map((t) => (
            <MenuItem key={t} value={t}>
              {t}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          label="Search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </Box>
      <Box display="grid" gap={2} gridTemplateColumns="repeat(auto-fill,minmax(300px,1fr))">
        {filtered.map((it) => (
          <Card key={it.url}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {it.title}
              </Typography>
              <Typography variant="body2">{it.summary}</Typography>
            </CardContent>
            <CardActions>
              <Button size="small" href={it.url} target="_blank">
                Open
              </Button>
              <Button size="small" onClick={() => setSummary(summarize(it.summary_raw || it.summary))}>
                Summarize
              </Button>
            </CardActions>
          </Card>
        ))}
      </Box>
      <Dialog open={Boolean(summary)} onClose={() => setSummary('')}>
        <DialogTitle>Summary</DialogTitle>
        <DialogContent>
          <Typography>{summary}</Typography>
        </DialogContent>
      </Dialog>
    </Box>
  );
}

export default Home;
