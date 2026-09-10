/* Catalogue content is loaded locally; source URLs remain available per product. */
window.equipmentCategory = 'microphones';
const gearCategories = [
  ['microphones', '麦克风', '人声与乐器收音'],
  ['interfaces', '声卡', '录音输入与音频输出'],
  ['preamps', '话放', '麦克风信号放大与音色处理'],
  ['headphones', '监听耳机', '录音监听与细节检查'],
  ['monitors', '监听音响', '工作室回放与混音监听'],
  ['plugins', '音频插件', '软件音效与声音制作']
];
function equipmentCatalogue() {
  const selected = gearCategories.find(c => c[0] === window.equipmentCategory) || gearCategories[0];
  const products = (window.gearProducts || []).filter(p => p.category === selected[0]);
  return `<div id="equipment-catalogue"><div class="filter-bar equipment-filters" role="group" aria-label="设备分类">${gearCategories.map(([id,label]) => `<button type="button" class="equipment-filter${id === selected[0] ? ' active' : ''}" data-gear-category="${id}" aria-pressed="${id === selected[0]}">${label}</button>`).join('')}</div><p class="equipment-count" role="status">${selected[1]} · ${products.length} 款产品</p><section class="equipment-grid curated-equipment" aria-label="${selected[1]}">${products.map(p => `<article class="equipment-card"><a class="equipment-image" href="${p.url}" target="_blank" rel="noopener noreferrer" aria-label="查看 ${p.name} 产品资料"><img src="${p.localImage}" alt="${p.name}" loading="lazy" width="600" height="400" /></a><div class="equipment-body"><span class="equipment-type">${selected[1]}</span><h3>${p.name}</h3><p>${selected[2]}</p><a class="gear-source" href="${p.url}" target="_blank" rel="noopener noreferrer">查看产品资料 <span aria-hidden="true">↗</span></a></div></article>`).join('')}</section></div>`;
}
document.addEventListener('click', event => {
  const button = event.target.closest('[data-gear-category]');
  if (!button) return;
  window.equipmentCategory = button.dataset.gearCategory;
  document.getElementById('equipment-catalogue').outerHTML = equipmentCatalogue();
  document.querySelector(`[data-gear-category="${window.equipmentCategory}"]`).focus({preventScroll:true});
});
const presetPhotography = {
  rap: ['7971866', '说唱歌手的舞台演出', 'https://www.pexels.com/photo/rapper-on-stage-with-microphone-7971866/'],
  backing: ['11044817', '录音室中的双人演唱与合作', 'https://www.pexels.com/photo/a-two-women-in-the-recording-studio-11044817/'],
  udg: ['8132774', '录音棚内的人声录制', 'https://www.pexels.com/photo/male-vocalist-recording-in-a-studio-8132774/'],
  pop: ['7087169', '流行人声录音现场', 'https://www.pexels.com/photo/a-singer-in-the-recording-studio-7087169/'],
  retro: ['10692897', '温暖的复古黑胶唱片机', 'https://www.pexels.com/photo/wooden-vinyl-record-player-10692897/'],
  electronic: ['8071910', '电子合成器的键盘与控制面板', 'https://www.pexels.com/photo/close-up-shot-of-an-electronic-synthesizer-8071910/']
};
function presetPhoto(id) {
  const photo = presetPhotography[id];
  return photo ? `<img class="preset-photograph" src="/assets/preset-photos/${id}.jpg" alt="${photo[1]}" width="900" height="600" loading="lazy" />` : '';
}
