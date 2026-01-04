// 在前端页面的开发者工具Console中运行此脚本

console.log('===== 清除缓存脚本 =====');

// 1. 清除所有localStorage
const lsCount = localStorage.length;
const lsKeys = [];
for (let i = 0; i < localStorage.length; i++) {
    lsKeys.push(localStorage.key(i));
}
localStorage.clear();
console.log(`✅ 清除了 ${lsCount} 个localStorage项:`, lsKeys);

// 2. 清除所有sessionStorage
const ssCount = sessionStorage.length;
sessionStorage.clear();
console.log(`✅ 清除了 ${ssCount} 个sessionStorage项`);

// 3. 清除可能的React Query缓存
try {
    if (window.__REACT_QUERY_CLIENT__) {
        window.__REACT_QUERY_CLIENT__.clear();
        console.log('✅ 清除了React Query缓存');
    }
} catch (e) {
    console.log('⚠️ React Query缓存未找到');
}

console.log('\n===== 缓存已清除 =====');
console.log('正在重新加载页面...\n');

// 4. 重新加载页面
setTimeout(() => {
    location.reload(true);
}, 1000);
