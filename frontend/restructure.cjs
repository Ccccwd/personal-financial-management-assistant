const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, 'src');

// 1. Create directories
const dirs = [
    'api',
    'components/common',
    'components/business',
    'components/layout',
    'views/auth',
    'views/dashboard',
    'views/transaction',
    'views/account',
    'views/statistics',
    'views/budget',
    'views/import',
    'views/settings',
    'router',
    'stores',
    'composables',
    'utils',
    'types',
    'styles'
];

dirs.forEach(d => {
    const fullPath = path.join(srcDir, d);
    if (!fs.existsSync(fullPath)) {
        fs.mkdirSync(fullPath, { recursive: true });
    }
});

// 2. Define Moves
const moves = [
    { from: 'layouts/MainLayout.vue', to: 'components/layout/MainLayout.vue' },
    { from: 'views/home/Dashboard.vue', to: 'views/dashboard/DashboardView.vue' },
    { from: 'views/auth/Login.vue', to: 'views/auth/LoginView.vue' },
    { from: 'views/auth/Register.vue', to: 'views/auth/RegisterView.vue' },
    { from: 'views/budget/BudgetList.vue', to: 'views/budget/BudgetView.vue' },
    { from: 'views/import/ImportData.vue', to: 'views/import/WechatImport.vue' },
    { from: 'views/settings/Profile.vue', to: 'views/settings/ProfileView.vue' },
    { from: 'views/statistics/Statistics.vue', to: 'views/statistics/StatisticsView.vue' },
    { from: 'utils/request.ts', to: 'api/request.ts' }
];

moves.forEach(({from, to}) => {
    const fromPath = path.join(srcDir, from);
    const toPath = path.join(srcDir, to);
    if (fs.existsSync(fromPath)) {
        fs.renameSync(fromPath, toPath);
        console.log(`Moved: ${from} -> ${to}`);
    }
});

// Clean up empty dirs
try { if (fs.existsSync(path.join(srcDir, 'layouts'))) fs.rmdirSync(path.join(srcDir, 'layouts')); } catch(e){}
try { if (fs.existsSync(path.join(srcDir, 'views/home'))) fs.rmdirSync(path.join(srcDir, 'views/home')); } catch(e){}

// 3. Define Placeholder Files
const placeholders = [
    "api/index.ts", 
    "components/common/AppHeader.vue", 
    "components/common/AppSidebar.vue", 
    "components/common/AppFooter.vue", 
    "components/common/LoadingSpinner.vue", 
    "components/common/EmptyState.vue", 
    "components/common/ConfirmDialog.vue",
    "components/business/TransactionCard.vue", 
    "components/business/CategoryIcon.vue", 
    "components/business/AccountSelector.vue", 
    "components/business/AmountInput.vue", 
    "components/business/DatePicker.vue", 
    "components/business/BudgetProgress.vue", 
    "components/business/TrendChart.vue", 
    "components/business/CategoryPieChart.vue", 
    "components/business/FileUploader.vue",
    "components/layout/AuthLayout.vue", 
    "components/layout/BlankLayout.vue",
    "views/transaction/TransactionDetail.vue",
    "views/account/AccountDetail.vue",
    "views/settings/SettingsView.vue", 
    "views/settings/CategoryManage.vue",
    "router/guards.ts",
    "stores/index.ts", 
    "stores/app.ts",
    "composables/useAuth.ts", 
    "composables/useTransaction.ts", 
    "composables/useStatistics.ts", 
    "composables/useNotification.ts",
    "utils/format.ts", 
    "utils/date.ts", 
    "utils/storage.ts", 
    "utils/validator.ts", 
    "utils/constants.ts",
    "styles/variables.scss", 
    "styles/reset.scss", 
    "styles/common.scss", 
    "styles/transitions.scss"
];

const vueTemplate = `<template>\n  <div>\n  </div>\n</template>\n\n<script setup lang="ts">\n</script>\n\n<style scoped>\n</style>\n`;
const tsTemplate = `// placeholder\n`;

placeholders.forEach(f => {
    const fullPath = path.join(srcDir, f);
    if (!fs.existsSync(fullPath)) {
        if (f.endsWith('.vue')) fs.writeFileSync(fullPath, vueTemplate, 'utf8');
        else fs.writeFileSync(fullPath, tsTemplate, 'utf8');
    }
});

// 4. Update import paths in all vue and ts files
function walk(dir) {
    let results = [];
    const list = fs.readdirSync(dir);
    list.forEach(file => {
        const fullPath = path.join(dir, file);
        const stat = fs.statSync(fullPath);
        if (stat && stat.isDirectory()) {
            results = results.concat(walk(fullPath));
        } else {
            if (file.endsWith('.vue') || file.endsWith('.ts')) {
                results.push(fullPath);
            }
        }
    });
    return results;
}

const allFiles = walk(srcDir);
const replacements = [
    { regex: /@\/utils\/request/g, target: '@/api/request' },
    { regex: /@\/layouts\/MainLayout\.vue/g, target: '@/components/layout/MainLayout.vue' },
    { regex: /@\/views\/home\/Dashboard\.vue/g, target: '@/views/dashboard/DashboardView.vue' },
    { regex: /@\/views\/auth\/Login\.vue/g, target: '@/views/auth/LoginView.vue' },
    { regex: /@\/views\/auth\/Register\.vue/g, target: '@/views/auth/RegisterView.vue' },
    { regex: /@\/views\/budget\/BudgetList\.vue/g, target: '@/views/budget/BudgetView.vue' },
    { regex: /@\/views\/import\/ImportData\.vue/g, target: '@/views/import/WechatImport.vue' },
    { regex: /@\/views\/settings\/Profile\.vue/g, target: '@/views/settings/ProfileView.vue' },
    { regex: /@\/views\/statistics\/Statistics\.vue/g, target: '@/views/statistics/StatisticsView.vue' },
    
    // Some routes might use the hardcoded names, adjust those too if any
    { regex: /views\/home\/Dashboard/g, target: 'views/dashboard/DashboardView' },
    { regex: /views\/auth\/Login/g, target: 'views/auth/LoginView' },
    { regex: /views\/auth\/Register/g, target: 'views/auth/RegisterView' },
    { regex: /views\/budget\/BudgetList/g, target: 'views/budget/BudgetView' },
    { regex: /views\/import\/ImportData/g, target: 'views/import/WechatImport' },
    { regex: /views\/settings\/Profile/g, target: 'views/settings/ProfileView' },
    { regex: /views\/statistics\/Statistics/g, target: 'views/statistics/StatisticsView' },
];

allFiles.forEach(file => {
    let content = fs.readFileSync(file, 'utf8');
    let original = content;
    replacements.forEach(r => {
        content = content.replace(r.regex, r.target);
    });
    if (content !== original) {
        fs.writeFileSync(file, content, 'utf8');
        console.log(`Updated imports in: ${path.relative(srcDir, file)}`);
    }
});

console.log("Restructure completed successfully.");
