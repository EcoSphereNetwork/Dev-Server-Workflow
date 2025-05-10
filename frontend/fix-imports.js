#!/usr/bin/env node

/**
 * Script to fix JavaScript/TypeScript imports after repository reorganization
 * Created as part of the Dev-Server-Workflow repository cleanup project
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Function to display section header
function section(title) {
  console.log('============================================================');
  console.log(`  ${title}`);
  console.log('============================================================');
  console.log('');
}

// Display welcome message
section('JavaScript/TypeScript Import Fixer');
console.log('This script will fix JavaScript/TypeScript imports after the repository reorganization.');
console.log('');

// Create a mapping of old to new import paths
section('Creating Import Mapping');
console.log('Creating a mapping of old to new import paths...');

const importMappings = [
  // Add mappings for frontend imports
  { from: '../src/components', to: '../src/components' },
  { from: '../src/utils', to: '../src/utils' },
  { from: '../src/services', to: '../src/services' },
  { from: '../src/hooks', to: '../src/hooks' },
  { from: '../src/context', to: '../src/context' },
  { from: '../src/api', to: '../src/api' },
  { from: '../src/types', to: '../src/types' },
  { from: '../src/constants', to: '../src/constants' },
  { from: '../src/assets', to: '../src/assets' },
  { from: '../src/styles', to: '../src/styles' },
  { from: '../src/pages', to: '../src/pages' },
  { from: '../src/layouts', to: '../src/layouts' },
  { from: '../src/routes', to: '../src/routes' },
  { from: '../src/store', to: '../src/store' },
  { from: '../src/reducers', to: '../src/store/reducers' },
  { from: '../src/actions', to: '../src/store/actions' },
  { from: '../src/selectors', to: '../src/store/selectors' },
  { from: '../src/middleware', to: '../src/store/middleware' },
  { from: '../src/sagas', to: '../src/store/sagas' },
  { from: '../src/thunks', to: '../src/store/thunks' },
  { from: '../src/api/mcp', to: '../src/api/mcp' },
  { from: '../src/api/n8n', to: '../src/api/n8n' },
  { from: '../src/api/openhands', to: '../src/api/openhands' },
  { from: '../src/api/github', to: '../src/api/github' },
  { from: '../src/api/gitlab', to: '../src/api/gitlab' },
  { from: '../src/api/openproject', to: '../src/api/openproject' },
  { from: '../src/api/appflowy', to: '../src/api/appflowy' },
  { from: '../src/api/affine', to: '../src/api/affine' },
];

console.log(`Created mapping with ${importMappings.length} entries.`);
console.log('');

// Find all JavaScript/TypeScript files
section('Finding JavaScript/TypeScript Files');
console.log('Finding all JavaScript/TypeScript files in the frontend directory...');

const jsFiles = execSync('find ./src -type f -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx"', { encoding: 'utf8' })
  .trim()
  .split('\n')
  .filter(Boolean);

console.log(`Found ${jsFiles.length} JavaScript/TypeScript files.`);
console.log('');

// Process each JavaScript/TypeScript file
section('Processing JavaScript/TypeScript Files');
console.log('Processing JavaScript/TypeScript files to fix imports...');

let updatedFiles = 0;

jsFiles.forEach(file => {
  console.log(`Processing ${file}...`);
  
  let content = fs.readFileSync(file, 'utf8');
  let originalContent = content;
  
  // Process each mapping
  importMappings.forEach(mapping => {
    const fromPattern = new RegExp(`from ['"](${mapping.from}|${mapping.from}/[^'"]+)['"]`, 'g');
    const importPattern = new RegExp(`import ['"](${mapping.from}|${mapping.from}/[^'"]+)['"]`, 'g');
    
    content = content.replace(fromPattern, match => {
      const importPath = match.match(/from ['"]([^'"]+)['"]/)[1];
      const relativePath = importPath.replace(mapping.from, mapping.to);
      return `from '${relativePath}'`;
    });
    
    content = content.replace(importPattern, match => {
      const importPath = match.match(/import ['"]([^'"]+)['"]/)[1];
      const relativePath = importPath.replace(mapping.from, mapping.to);
      return `import '${relativePath}'`;
    });
  });
  
  // Check if the file has changed
  if (content !== originalContent) {
    console.log(`  Imports updated in ${file}`);
    fs.writeFileSync(file, content, 'utf8');
    updatedFiles++;
  } else {
    console.log(`  No changes needed in ${file}`);
  }
});

console.log('');
console.log(`Updated imports in ${updatedFiles} files.`);
console.log('');

section('Import Fixing Complete');
console.log('The import fixing process is now complete.');
console.log('Please review the changes and test the code to ensure everything works correctly.');
console.log('');
console.log('Thank you for using the JavaScript/TypeScript Import Fixer script.');