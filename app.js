const API_CONFIG = {
  agentEndpoint: '/api/agent/chat',
  resourcesEndpoint: '/api/resources/search',
  userEndpoint: '/api/users/me'
};

const people = {
  recording: [
    { id:'lin-wei', name:'林维', role:'高级录音师', styles:['流行','说唱','民谣'], price:'500 元/首', image:'https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=900&q=80', exp:'8 年录音棚经验', works:'128 首完成作品', intro:'专注人声细节与现场氛围的平衡，服务过独立音乐人和商业配唱项目。', skills:['人声录制','乐器录制','录音棚制作','现场指导'], prices:[['基础录音','500 元 / 首'],['精修录音','800 元 / 首']] },
    { id:'chen-yi', name:'陈一', role:'资深录音师', styles:['流行','R&B','广告配音'], price:'650 元/首', image:'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?auto=format&fit=crop&w=900&q=80', exp:'10 年录制经验', works:'196 首完成作品', intro:'擅长捕捉干净、稳定且有质感的人声，熟悉各类商业音频制作流程。', skills:['人声制作','配音录制','和声设计','音色管理'], prices:[['基础录音','650 元 / 首'],['商业配唱','1,200 元 / 首']] },
    { id:'yuan-he', name:'袁赫', role:'录音制作人', styles:['摇滚','民谣','乐队'], price:'720 元/首', image:'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=900&q=80', exp:'9 年乐队录制经验', works:'87 张专辑项目', intro:'重视真实动态和演奏现场感，从前期录制到制作统筹提供一体化支持。', skills:['鼓组录制','吉他录制','乐队同期','制作统筹'], prices:[['同期录音','720 元 / 首'],['乐队制作','2,800 元 / 首']] }
  ],
  mixing: [
    { id:'luo-xin', name:'罗昕', role:'高级混音师', styles:['Hip-Hop','流行','电子'], price:'1,500 元/首', image:'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=900&q=80', exp:'12 年混音经验', works:'340+ 混音项目', intro:'以强劲、开阔、具备商业完成度的声音为目标，尤其擅长说唱和流行人声塑形。', skills:['人声处理','EQ 调整','压缩处理','空间效果设计'], prices:[['基础混音','1,000 元 / 首'],['高级混音','3,000 元 / 首']] },
    { id:'zhou-mo', name:'周默', role:'混音工程师', styles:['摇滚','电子','影视'], price:'1,800 元/首', image:'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=900&q=80', exp:'11 年混音经验', works:'100+ 影视音乐项目', intro:'擅长复杂编制的层次处理和动态控制，让作品在不同播放设备上保持清晰度。', skills:['总线处理','动态控制','电子音色','母带预处理'], prices:[['基础混音','1,200 元 / 首'],['完整制作','3,200 元 / 首']] },
    { id:'jia-ning', name:'贾宁', role:'音乐混音师', styles:['R&B','流行','民谣'], price:'1,200 元/首', image:'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?auto=format&fit=crop&w=900&q=80', exp:'7 年混音经验', works:'210 首发行作品', intro:'强调情绪、空间和声音的自然呼吸感，善于为抒情人声建立细腻层次。', skills:['人声润色','氛围设计','频段整理','立体声像'], prices:[['基础混音','1,000 元 / 首'],['人声精修','1,800 元 / 首']] }
  ],
  arrangement: [
    { id:'shen-yu', name:'沈予', role:'编曲制作人', styles:['流行编曲','影视配乐','电子'], price:'2,000 元起', image:'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=900&q=80', exp:'14 年制作经验', works:'260 首作品发行', intro:'在流行旋律和电子质感之间建立平衡，为歌曲提供完整、可发行的编曲方案。', skills:['流行编曲','音色设计','影视配乐','制作统筹'], prices:[['基础编曲','2,000 元'],['高级制作','5,000 元']] },
    { id:'deng-qi', name:'邓祺', role:'编曲师', styles:['说唱编曲','Trap','R&B'], price:'2,400 元起', image:'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=900&q=80', exp:'8 年制作经验', works:'170+ Beat 制作', intro:'专注现代律动和低频设计，适合说唱、R&B 及融合型流行音乐。', skills:['Beat 制作','鼓组编排','采样设计','人声 Chop'], prices:[['基础 Beat','2,400 元'],['定制制作','5,500 元']] },
    { id:'an-chen', name:'安辰', role:'作曲 / 编曲师', styles:['民谣','国风','流行'], price:'1,800 元起', image:'https://images.unsplash.com/photo-1531384441138-2736e62e0919?auto=format&fit=crop&w=900&q=80', exp:'9 年制作经验', works:'72 部影视配乐', intro:'从旋律情绪出发，打造有画面感与叙事感的东方流行声音。', skills:['国风配器','弦乐写作','旋律创作','影视音乐'], prices:[['基础编曲','1,800 元'],['影视配乐','4,800 元']] }
  ],
  live: [
    { id:'he-yan', name:'何言', role:'直播音频工程师', styles:['声卡调试','直播优化','插件配置'], price:'500 元起', image:'https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=900&q=80', exp:'服务 1,200+ 直播间', works:'92% 一次调试通过', intro:'针对直播平台、房间环境和设备链路做细致调校，解决闷、喷麦、延迟等常见问题。', skills:['声卡调试','麦克风调试','插件安装','平台推流'], prices:[['基础调试','500 元'],['高级方案','1,500 元']] },
    { id:'xiao-hao', name:'肖昊', role:'音频系统工程师', styles:['唱歌直播','K 歌','现场扩声'], price:'680 元起', image:'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=900&q=80', exp:'6 年系统调试经验', works:'330 套设备方案', intro:'面向唱歌主播和小型演出场景，着重改善返听、混响和演唱舒适度。', skills:['唱歌直播','返听系统','混响设计','设备选型'], prices:[['基础调试','680 元'],['设备方案','1,600 元']] },
    { id:'yan-ting', name:'严亭', role:'直播技术顾问', styles:['电商直播','语音直播','远程调试'], price:'420 元起', image:'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=900&q=80', exp:'合作 80+ 品牌直播间', works:'远程支持 7 x 12', intro:'通过远程诊断快速定位链路问题，为语音及电商直播提供稳定、清晰的声音保障。', skills:['远程支持','降噪设置','人声优化','电商直播'], prices:[['远程诊断','420 元'],['整套优化','1,200 元']] }
  ]
};

const services = [
  ['录音服务','专业录音棚、人声与乐器录制','mic-vocal','/recording'],['混音服务','从人声到母带的细节打磨','sliders-horizontal','/mixing'],['直播调试','直播间声音和设备链路优化','radio','/live'],['编曲服务','为旋律构建完整音乐表达','music-3','/arrangement'],['设备供应','按场景匹配专业音频设备','headphones','/equipment'],['AI 智能体','用一句话开启资源匹配','sparkles','/ai-agent']
];
const equipment = [
  ['麦克风','AT2020 XLR','1,000 - 1,600 元','翻唱、配音、新手创作','https://images.unsplash.com/photo-1590602847861-f357a9332bbc?auto=format&fit=crop&w=700&q=80'],['声卡','Rodecaster Duo','3,000 - 4,000 元','直播、播客、多人录制','https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=700&q=80'],['监听设备','Yamaha HS5','2,000 - 3,000 元','家庭工作室、混音入门','https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=700&q=80'],['耳机','DT 770 Pro','1,000 - 1,500 元','录音监听、音乐制作','https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=700&q=80'],['音频插件','FabFilter Bundle','1,500 - 3,000 元','混音、人声处理、母带','https://images.unsplash.com/photo-1558403194-611308249627?auto=format&fit=crop&w=700&q=80']];

function icon(name){ return `<i data-lucide="${name}"></i>`; }
function link(href, content, className=''){ return `<a href="${href}" class="${className}" data-route>${content}</a>`; }
function header(){ const path=location.pathname; return `<header class="shell topbar"><a class="brand" href="/" data-route><span class="brand-mark">${icon('audio-lines')}</span><span>智声科技</span></a><nav class="nav"><a class="${path=='/'?'active':''}" href="/" data-route>首页</a><a class="${path=='/recording'?'active':''}" href="/recording" data-route>资源服务</a><a class="${path=='/equipment'?'active':''}" href="/equipment" data-route>设备供应</a><a class="nav-ai ${path=='/ai-agent'?'active':''}" href="/ai-agent" data-route>${icon('sparkles')} AI 智能体</a></nav><button class="icon-button" title="通知">${icon('bell')}</button></header>`; }
function footer(){ return `<footer class="shell footer">ZHISHENG TECHNOLOGY / AI AUDIO RESOURCE MATCHING PLATFORM</footer>`; }
function tags(items){ return `<div class="tags">${items.map(x=>`<span class="tag">${x}</span>`).join('')}</div>`; }
function personCard(person, kind){ return `<article class="person-card"><div class="person-cover"><img src="${person.image}" alt="${person.name}"/><span class="role-tag">${person.role}</span></div><div class="person-body"><div class="person-name"><h3>${person.name}</h3><span class="verified" title="已认证">${icon('badge-check')}</span></div><p class="person-role">${person.exp}</p>${tags(person.styles)}<div class="price-row"><div><small>${kind==='live'?'基础调试':'服务起价'}</small><strong>${person.price}</strong></div>${link(`/${kind}/${person.id}`,`查看详情 ${icon('arrow-up-right')}`,'text-link')}</div></div></article>`; }
function home(){ return `<main><section class="shell hero"><div><div class="eyebrow">AI AUDIO RESOURCE MATCHING</div><h1>让每一段声音，<br/>找到<span>对的人</span>。</h1><p class="hero-copy">智声科技连接专业音频人才、制作服务与设备资源。用 AI 理解你的创作意图，将声音制作从寻找开始变得更准确。</p><div class="hero-actions">${link('/ai-agent',`立即智能匹配 ${icon('arrow-up-right')}`,'btn btn-primary')}${link('/recording',`浏览专业资源 ${icon('search')}`,'btn btn-secondary')}</div></div><div class="hero-visual"><span class="studio-label">STUDIO_07 / ONLINE</span><div class="visual-bottom"><div><strong>声音，正在被听见</strong><p>连接每一个专业创作时刻</p></div><div class="signal">${'<b></b>'.repeat(8)}</div></div></div></section><div class="shell trust-row"><span>覆盖音频制作全流程</span><strong>180+ 专业人才</strong><strong>500+ 服务案例</strong><strong>24h 智能响应</strong></div><section class="shell section"><div class="section-head"><div><div class="eyebrow">RESOURCE NETWORK</div><h2>为创作的每一步找到支持</h2></div><p>从第一句人声到作品发布，按需求、风格和预算连接恰当的专业资源。</p></div><div class="service-grid">${services.map(([title,desc,ico,path])=>link(path,`<span class="service-icon">${icon(ico)}</span><h3>${title}</h3><p>${desc}</p><span class="card-arrow">${icon('arrow-up-right')}</span>`,'service-card')).join('')}</div></section><section class="shell feature-band"><div><div class="eyebrow">INTELLIGENT MATCHING</div><h2>描述你的声音需求，剩下交给 AI。</h2><p>输入预算、风格、用途或已有设备，即刻得到面向实际制作流程的资源建议。</p></div>${link('/ai-agent',`进入 AI 智能体 ${icon('sparkles')}`,'btn btn-primary')}</section></main>`; }
function listing(kind, title, description){ return `<main class="shell page"><section class="page-title"><div class="eyebrow">${kind.toUpperCase()} / CURATED</div><h1>${title}</h1><p>${description}</p></section><div class="filter-bar"><button class="filter active">全部</button><button class="filter">流行</button><button class="filter">说唱</button><button class="filter">电子</button><button class="filter">高评分</button><button class="filter">预算友好</button></div><section class="people-grid">${people[kind].map(p=>personCard(p,kind)).join('')}</section></main>`; }
function detail(kind,id){ const person=people[kind]?.find(p=>p.id===id); if(!person) return notFound(); const roleNames={recording:'录音服务',mixing:'混音服务',arrangement:'编曲服务',live:'直播调试'}; const works=kind==='mixing'?['霓虹夜行','没有你的周末','Be Right Back']:['Demo Session 01','Live Room Take','Untitled, V3']; return `<main class="shell"><section class="detail-hero"><div class="detail-photo"><img src="${person.image}" alt="${person.name}"/></div><div class="detail-intro"><div class="eyebrow">${roleNames[kind]} / VERIFIED</div><h1>${person.name}</h1><div class="tags">${tags(person.styles)}</div><p>${person.intro}</p><div class="detail-stats"><div class="detail-stat"><span>专业经验</span><strong>${person.exp}</strong></div><div class="detail-stat"><span>项目履历</span><strong>${person.works}</strong></div><div class="detail-stat"><span>响应状态</span><strong>可预约</strong></div></div>${link('/ai-agent',`让 AI 协助匹配 ${icon('sparkles')}`,'btn btn-primary')}</div></section><section class="detail-grid"><div><div class="detail-section"><h2>个人介绍</h2><p>${person.intro} 以清晰的沟通和可执行的制作建议，帮助创作者让声音更接近心中的想象。</p></div><div class="detail-section"><h2>${kind==='mixing'?'技术能力':'专业能力'}</h2><div class="skill-list">${person.skills.map(x=>`<div class="skill-item">${x}</div>`).join('')}</div></div><div class="detail-section"><h2>作品试听</h2>${works.map((w,i)=>`<div class="track"><button class="track-play" title="播放试听" data-play>${icon('play')}</button><div class="track-info"><strong>${w}</strong><span>PREVIEW / 0${i+2}:${i?'48':'36'}</span></div><div class="wave">${'<b></b>'.repeat(22)}</div></div>`).join('')}</div></div><aside class="pricing"><div class="pricing-head"><h3>服务价格</h3></div>${person.prices.map(p=>`<div class="price-item"><span>${p[0]}</span><strong>${p[1]}</strong></div>`).join('')}<button class="btn btn-primary" data-contact>咨询档期 ${icon('message-circle')}</button></aside></section></main>`; }
function equipmentPage(){ return `<main class="shell page"><section class="page-title"><div class="eyebrow">EQUIPMENT / CURATED</div><h1>设备供应与选型</h1><p>从直播入门到家庭工作室，按预算与实际使用场景提供更合适的设备组合。</p></section><div class="filter-bar"><button class="filter active">全部设备</button><button class="filter">麦克风</button><button class="filter">声卡</button><button class="filter">监听设备</button><button class="filter">耳机</button><button class="filter">音频插件</button></div><section class="equipment-grid">${equipment.map(e=>`<article class="equipment-card"><div class="equipment-image"><img src="${e[4]}" alt="${e[1]}"/></div><div class="equipment-body"><span class="equipment-type">${e[0]}</span><h3>${e[1]}</h3><p>适合：${e[3]}</p><span class="equipment-price">${e[2]}</span></div></article>`).join('')}</section><section class="consult"><div class="consult-head"><div><div class="eyebrow">AI EQUIPMENT GUIDE</div><h2>告诉我你的使用场景</h2><p>例如：我是新手主播，预算 3000 元，需要一套直播设备。</p></div><span class="service-icon">${icon('headphones')}</span></div><div class="consult-form"><input id="consultInput" aria-label="设备需求" placeholder="输入预算、用途或已有设备"/><button class="btn btn-primary" id="consultButton">获取建议 ${icon('arrow-up-right')}</button></div><div id="consultResult" class="consult-result"></div></section></main>`; }
function agentPage(){ return `<main class="shell chat-shell"><aside class="chat-side"><button class="btn btn-secondary chat-new" id="newChat">${icon('square-pen')} 新建对话</button><p class="side-label">当前对话</p><div class="thread">音频资源智能匹配</div><p class="side-note">智声 AI 将基于需求、预算和风格，为你匹配平台内的专业资源。</p></aside><section class="chat-main"><header class="chat-header"><div><strong>智声 AI 智能体</strong><span>音频行业资源匹配助手</span></div><span class="status">READY</span></header><div class="messages" id="messages"><div class="message"><div class="message-avatar">${icon('sparkles')}</div><div class="bubble">你好，我是智声 AI。告诉我你想制作什么，或描述你的预算、风格和设备需求。</div></div></div><div class="chat-input-wrap"><div class="suggestions"><button data-suggest="我需要一个适合制作说唱的混音师">找说唱混音师</button><button data-suggest="预算 3000 元，推荐直播设备">推荐直播设备</button><button data-suggest="我想做一首流行歌曲，需要什么编曲">制定制作方案</button></div><form class="chat-input" id="chatForm"><input id="chatInput" autocomplete="off" placeholder="描述你的音频需求..."/><button class="send" title="发送" type="submit">${icon('arrow-up')}</button></form></div></section></main>`; }
function notFound(){ return `<main class="shell empty"><div class="eyebrow">404 / NOT FOUND</div><h1>这个声音还没有被收录</h1><p>返回首页，继续探索专业音频资源。</p>${link('/',`回到首页 ${icon('arrow-right')}`,'btn btn-primary')}</main>`; }
function app(){ const path=location.pathname.replace(/\/$/,'')||'/'; let content=''; const match=path.match(/^\/(recording|mixing|arrangement|live)\/([^/]+)$/); if(match) content=detail(match[1],match[2]); else if(path==='/') content=home(); else if(['recording','mixing','arrangement','live'].includes(path.slice(1))) { const map={recording:['录音服务','在专业录音环境中捕捉每一个有表现力的瞬间。'],mixing:['混音服务','让作品在每一副耳机、每一台音箱里都有准确表达。'],arrangement:['编曲服务','从灵感雏形到完整制作，让旋律拥有自己的世界。'],live:['直播调试','让直播间的每一句声音都清晰、稳定、恰到好处。']}; content=listing(path.slice(1),...map[path.slice(1)]); } else if(path==='/equipment') content=equipmentPage(); else if(path==='/ai-agent') content=agentPage(); else content=notFound(); document.querySelector('#app').innerHTML=header()+content+(path!=='/ai-agent'?footer():''); lucide.createIcons(); bindEvents(); window.scrollTo({top:0,behavior:'instant'}); }
function navigate(url){ history.pushState({},'',url); app(); }
function aiReply(query){ const q=query.toLowerCase(); if(/说唱|hip|rap|混音/.test(q)){ return { text:'根据你的风格需求，我优先匹配擅长 Hip-Hop 人声塑形与低频控制的混音师。', person:people.mixing[0], kind:'mixing' }; } if(/设备|主播|直播|声卡|麦克风/.test(q)){ return { text:'你的需求更适合一套以人声清晰度和易用性为核心的直播组合：电容麦克风 + 双通道声卡 + 封闭式监听耳机。预算 3000 元内可以优先考虑 AT2020 XLR、基础声卡和 DT 770 Pro。' }; } if(/编曲|歌曲|流行/.test(q)){ return { text:'建议先确定参考曲和情绪方向，再由编曲师完成节奏骨架、和声、音色设计和人声空间预留。沈予适合现代流行与电子质感的完整制作。', person:people.arrangement[0], kind:'arrangement' }; } return { text:'我已理解你的需求。为了匹配更准确的资源，请补充期望风格、预算范围、用途和交付时间，我会基于平台资源给出优先建议。' }; }
function addMessage(role,content){ const box=document.querySelector('#messages'); if(!box)return; const avatar=role==='user'?'U':icon('sparkles'); box.insertAdjacentHTML('beforeend',`<div class="message ${role}">${role==='user'?'':`<div class="message-avatar">${avatar}</div>`}<div class="bubble">${content}</div></div>`); lucide.createIcons(); box.parentElement.scrollTop=box.scrollHeight; }
function bindEvents(){ document.querySelectorAll('[data-route]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();navigate(a.getAttribute('href'));})); document.querySelectorAll('[data-play]').forEach(btn=>btn.addEventListener('click',()=>{ const track=btn.closest('.track'); const playing=track.classList.toggle('playing'); btn.innerHTML=icon(playing?'pause':'play'); lucide.createIcons(); })); document.querySelectorAll('[data-contact]').forEach(btn=>btn.addEventListener('click',()=>navigate('/ai-agent'))); document.querySelectorAll('.filter').forEach(btn=>btn.addEventListener('click',()=>{btn.parentElement.querySelectorAll('.filter').forEach(x=>x.classList.remove('active'));btn.classList.add('active')})); const consult=document.querySelector('#consultButton'); if(consult)consult.addEventListener('click',()=>{const input=document.querySelector('#consultInput');const result=document.querySelector('#consultResult');result.textContent=input.value?`建议先从「人声麦克风 + 声卡 + 监听耳机」的组合开始。根据“${input.value}”，AI 将优先筛选预算友好、易于上手且适合直播场景的设备。`:'请告诉我你的预算、使用场景或已有设备。';result.classList.add('show');}); const form=document.querySelector('#chatForm'); if(form)form.addEventListener('submit',e=>{e.preventDefault();const input=document.querySelector('#chatInput');const q=input.value.trim();if(!q)return;addMessage('user',q);input.value='';setTimeout(()=>{const r=aiReply(q);let c=`${r.text}`;if(r.person)c+=`<div class="recommend"><div class="rec-top"><img class="rec-photo" src="${r.person.image}" alt="${r.person.name}"/><div><strong>${r.person.name}</strong><span>${r.person.role}</span></div></div><div class="rec-meta"><span>${r.person.price}</span><span>${r.person.styles.join(' / ')}</span></div>${link(`/${r.kind}/${r.person.id}`,`查看详情 ${icon('arrow-up-right')}`,'text-link')}</div>`;addMessage('ai',c);},420);}); document.querySelectorAll('[data-suggest]').forEach(btn=>btn.addEventListener('click',()=>{const input=document.querySelector('#chatInput');input.value=btn.dataset.suggest;input.focus();})); const newChat=document.querySelector('#newChat'); if(newChat)newChat.addEventListener('click',()=>{document.querySelector('#messages').innerHTML=`<div class="message"><div class="message-avatar">${icon('sparkles')}</div><div class="bubble">新的对话已开始。请告诉我你的音频需求。</div></div>`;lucide.createIcons();}); }
window.addEventListener('popstate',app);

// DeepSeek streaming chat: the browser only talks to our own /api/chat proxy.
const CHAT_API_URL = window.CHAT_API_URL || '/api/chat';
const chatHistory = [];

function escapeChatText(value) {
  return String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}

function appendStreamMessage(role, text = '') {
  const box = document.querySelector('#messages');
  if (!box) return null;
  const isUser = role === 'user';
  const message = document.createElement('div');
  message.className = `message ${isUser ? 'user' : 'ai'}`;
  if (!isUser) {
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = icon('sparkles');
    message.appendChild(avatar);
  }
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;
  message.appendChild(bubble);
  box.appendChild(message);
  if (!isUser) lucide.createIcons();
  message.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  return bubble;
}

function parseDeepSeekEvent(raw) {
  const data = raw.replace(/^data:\s*/, '').trim();
  if (!data || data === '[DONE]') return '';
  try {
    const payload = JSON.parse(data);
    return payload.choices?.[0]?.delta?.content || '';
  } catch {
    return '';
  }
}

async function streamDeepSeekReply(messages, bubble) {
  const response = await fetch(CHAT_API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
    body: JSON.stringify({ model: 'deepseek-chat', messages })
  });
  if (!response.ok) {
    let message = `请求失败（${response.status}）`;
    try { message = (await response.json()).error || message; } catch {}
    throw new Error(message);
  }
  if (!response.body) throw new Error('浏览器不支持流式响应');
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let pending = '';
  let answer = '';
  while (true) {
    const { value, done } = await reader.read();
    pending += decoder.decode(value || new Uint8Array(), { stream: !done });
    const events = pending.split(/\n\n/);
    pending = events.pop() || '';
    for (const event of events) {
      const piece = parseDeepSeekEvent(event);
      if (piece) {
        answer += piece;
        bubble.textContent = answer;
      }
    }
    if (done) break;
  }
  if (pending) {
    const piece = parseDeepSeekEvent(pending);
    answer += piece;
    bubble.textContent = answer;
  }
  return answer;
}

// -----------------------------------------------------------------------------
// AI Mixing demo: a separate upload/job experience that does not touch /ai-agent.
// -----------------------------------------------------------------------------
const MIXING_JOB_KEY = 'zhisheng-active-mix-job-v1';
const MIXING_API_BASE = (window.MIXING_API_BASE || 'https://zhisheng-ai-298879-11-1470821727.sh.run.tcloudbase.com').replace(/\/$/, '');
const mixingApiUrl = path => `${MIXING_API_BASE}/api/mixing${path}`;
const mixingState = { files: {}, job: null, pollTimer: null };
const mixingRoles = [
  ['accompaniment', '伴奏（accompaniment）', 'music-2'],
  ['vocal', '主人声（vocal）', 'mic-vocal']
];
const mixingStatuses = [
  ['uploading', '上传音频'], ['planning', 'AI 分析'], ['queued', '等待工作站'],
  ['claimed', '任务已领取'], ['preparing', '准备工作区'], ['studio_processing', '专业混音处理中'],
  ['exporting', '导出最终音频'], ['uploading_result', '上传混音结果'], ['completed', 'AI 混音完成']
];

function aiMixingPage() {
  return `<main class="shell mixing-page">
    <section class="mixing-hero"><div><div class="eyebrow">AI AUDIO / MIXING LAB</div><h1>AI 智能混音</h1><p>让 AI 理解音乐，让专业混音经验自动执行。</p><div class="mixing-mode"><span class="mode-dot"></span> 测试执行模式 / Studio One Agent Ready</div></div><div class="mixing-hero-art"><div class="mix-orbit orbit-a"></div><div class="mix-orbit orbit-b"></div><span>${icon('sliders-horizontal')}</span><b>${icon('waveform')}</b></div></section>
    <section class="mixing-layout"><div class="mixing-panel"><div class="panel-kicker">01 / AUDIO SOURCES</div><h2>上传你的音频素材</h2><p class="panel-help">最多 4 个 WAV 或 MP3 文件，分别放入对应轨道。第一阶段模板统一使用 ZHISHENG_DEFAULT_MIX。</p><div class="mix-upload-grid">${mixingRoles.map(([role, label, ico]) => `<label class="mix-drop" data-mix-drop="${role}"><input class="mix-file-input" data-mix-input="${role}" type="file" accept="audio/wav,audio/x-wav,audio/mpeg,.wav,.mp3"/><span class="mix-drop-icon">${icon(ico)}</span><strong>${label}</strong><small>拖拽或点击上传</small><span class="mix-file-meta" data-mix-meta="${role}">尚未选择文件</span></label>`).join('')}</div><div class="mix-plan-fields"><label><span>音乐类型</span><select id="mixGenre"><option value="AI 自动判断">AI 自动判断</option><option value="流行">流行</option><option value="说唱 / Hip-Hop">说唱 / Hip-Hop</option><option value="民谣">民谣</option><option value="直播人声">直播人声</option></select></label><label class="mix-prompt-field"><span>告诉 AI 你希望这首歌是什么感觉</span><textarea id="mixPrompt" rows="3" placeholder="例如：想要人声更有力量，比较贴脸。"></textarea></label></div><div class="mix-actions"><button class="btn btn-primary" id="startMixing">${icon('sparkles')} 开始 AI 智能混音</button><span id="mixFormError" class="mix-error" role="alert"></span></div></div><aside class="mix-status-panel" id="mixStatusPanel"><div class="panel-kicker">02 / MIX JOB</div><h2>任务状态</h2><div class="mix-job-id" id="mixJobId">等待创建任务</div><div class="mix-timeline" id="mixTimeline">${mixingStatuses.map(([status, label]) => `<div class="mix-step" data-mix-step="${status}"><span class="step-mark"></span><span>${label}</span></div>`).join('')}</div><div class="mix-plan-card" id="mixPlanCard"><span>混音方案</span><strong>ZHISHENG_DEFAULT_MIX</strong><p>AI 计划将在创建任务后显示。</p></div><div class="mix-result" id="mixResult"></div></aside></section>
  </main>`;
}

function formatMixBytes(value) {
  if (!Number.isFinite(value)) return '';
  return `${(value / (1024 * 1024)).toFixed(value > 1024 * 1024 ? 1 : 2)} MB`;
}

function setMixError(message = '') {
  const element = document.querySelector('#mixFormError');
  if (element) element.textContent = message;
}

function readMixFileInfo(file) {
  return new Promise(resolve => {
    const audio = document.createElement('audio');
    audio.preload = 'metadata';
    const url = URL.createObjectURL(file);
    audio.onloadedmetadata = () => { const duration = Number.isFinite(audio.duration) ? audio.duration : null; URL.revokeObjectURL(url); resolve(duration); };
    audio.onerror = () => { URL.revokeObjectURL(url); resolve(null); };
    audio.src = url;
  });
}

async function selectMixFile(role, file) {
  setMixError('');
  if (!file) return;
  const ext = (file.name.split('.').pop() || '').toLowerCase();
  if (!['wav', 'mp3'].includes(ext)) { setMixError('格式不支持，仅允许 WAV 或 MP3。'); return; }
  if (file.size > 100 * 1024 * 1024) { setMixError('文件过大，单个文件不能超过 100 MB。'); return; }
  const duration = await readMixFileInfo(file);
  if (duration === null) { setMixError('无法读取音频信息，请检查文件是否损坏。'); return; }
  mixingState.files[role] = { role, file, duration };
  const meta = document.querySelector(`[data-mix-meta="${role}"]`);
  if (meta) meta.textContent = `${file.name} · ${formatMixBytes(file.size)} · ${ext.toUpperCase()} · ${Math.round(duration)}s`;
  document.querySelector(`[data-mix-drop="${role}"]`)?.classList.add('has-file');
}

function renderMixJob(job) {
  mixingState.job = job;
  sessionStorage.setItem(MIXING_JOB_KEY, job.job_id);
  const id = document.querySelector('#mixJobId');
  if (id) id.textContent = `${job.job_id} · ${job.status}`;
  document.querySelectorAll('[data-mix-step]').forEach(step => {
    const target = step.dataset.mixStep;
    const currentIndex = mixingStatuses.findIndex(item => item[0] === job.status);
    const targetIndex = mixingStatuses.findIndex(item => item[0] === target);
    step.classList.toggle('done', targetIndex < currentIndex || job.status === 'completed');
    step.classList.toggle('current', target === job.status || (job.status === 'completed' && target === 'completed'));
    step.classList.toggle('failed', job.status === 'failed' && target === job.progress?.step);
  });
  const plan = document.querySelector('#mixPlanCard');
  if (plan) plan.innerHTML = `<span>AI 混音方案 · ${job.plan?.genre || 'UNKNOWN'}</span><strong>${job.plan?.template_id || 'ZHISHENG_DEFAULT_MIX'}</strong><p>${escapeChatText(job.plan?.reason || '已生成默认专业混音方案。')}</p>`;
  const result = document.querySelector('#mixResult');
  if (result && job.status === 'completed' && job.result?.download_url) {
    const formatLabel = (job.result.format || 'wav').toUpperCase();
    const resultUrl = job.result.download_url.startsWith('/api/mixing') ? `${MIXING_API_BASE}${job.result.download_url}` : job.result.download_url;
    result.innerHTML = `<div class="result-badge">${icon('check-circle-2')} AI 混音完成</div><strong>${escapeChatText(job.result.display_name || `zhisheng_mix.${formatLabel.toLowerCase()}`)}</strong><small>${job.result.execution_mode === 'manual_test' ? '测试执行模式：测试输出文件' : `执行模式：${job.result.execution_mode || 'studio_one'}`}</small><audio controls preload="metadata" src="${resultUrl}"></audio><a class="btn btn-primary" href="${resultUrl}" download>${icon('download')} 下载 ${formatLabel}</a>`;
    lucide.createIcons();
    if (mixingState.pollTimer) clearInterval(mixingState.pollTimer);
  } else if (result && job.status === 'failed') {
    result.innerHTML = `<div class="result-badge failed-badge">${icon('circle-alert')} 任务失败</div><p>${escapeChatText(job.error || job.progress?.message || 'Local Agent 执行失败')}</p>`;
    lucide.createIcons();
    if (mixingState.pollTimer) clearInterval(mixingState.pollTimer);
  } else if (result) {
    result.innerHTML = `<span class="mix-live-dot"></span>${escapeChatText(job.progress?.message || '任务正在等待处理')}`;
  }
}

async function pollMixJob(jobId) {
  try {
    const response = await fetch(mixingApiUrl(`/jobs/${encodeURIComponent(jobId)}`));
    if (!response.ok) throw new Error('任务状态暂时无法读取');
    const payload = await response.json();
    if (payload.job) renderMixJob(payload.job);
  } catch (error) { setMixError(error.message); }
}

function startMixPolling(jobId) {
  if (mixingState.pollTimer) clearInterval(mixingState.pollTimer);
  pollMixJob(jobId);
  mixingState.pollTimer = setInterval(() => pollMixJob(jobId), 3000);
}

async function createMixJob() {
  const files = Object.values(mixingState.files);
  const error = document.querySelector('#mixFormError');
  const button = document.querySelector('#startMixing');
  if (files.length !== 2 || !mixingState.files.accompaniment || !mixingState.files.vocal) { setMixError('请同时上传伴奏和主人声。'); return; }
  if (button) { button.disabled = true; button.innerHTML = `${icon('loader-circle')} 正在上传并分析`; lucide.createIcons(); }
  try {
    const uploads = [];
    for (const item of files) {
      const form = new FormData(); form.append('file', item.file); form.append('role', item.role);
      const response = await fetch(mixingApiUrl('/uploads'), { method: 'POST', body: form });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || '上传失败');
      uploads.push({ file_id: payload.file.file_id, role: item.role });
    }
    const response = await fetch(mixingApiUrl('/jobs'), {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        uploads,
        genre_hint: document.querySelector('#mixGenre')?.value || 'AI 自动判断',
        user_prompt: document.querySelector('#mixPrompt')?.value || '',
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || '创建任务失败');
    renderMixJob(payload.job); startMixPolling(payload.job.job_id);
  } catch (error) { setMixError(error.message); }
  finally { if (button) { button.disabled = false; button.innerHTML = `${icon('sparkles')} 开始 AI 智能混音`; lucide.createIcons(); } }
}

function initAiMixingPage() {
  if (!document.querySelector('.mixing-page')) return;
  document.querySelectorAll('[data-mix-input]').forEach(input => input.addEventListener('change', event => selectMixFile(input.dataset.mixInput, event.target.files[0])));
  document.querySelectorAll('[data-mix-drop]').forEach(drop => {
    drop.addEventListener('dragover', event => { event.preventDefault(); drop.classList.add('dragging'); });
    drop.addEventListener('dragleave', () => drop.classList.remove('dragging'));
    drop.addEventListener('drop', event => { event.preventDefault(); drop.classList.remove('dragging'); selectMixFile(drop.dataset.mixDrop, event.dataTransfer.files[0]); });
  });
  document.querySelector('#startMixing')?.addEventListener('click', createMixJob);
  const existing = sessionStorage.getItem(MIXING_JOB_KEY);
  if (existing) startMixPolling(existing);
}

function mountAiMixingPage() {
  document.querySelector('#app').innerHTML = header() + aiMixingPage();
  document.querySelector('.mix-plan-fields')?.remove();
  lucide.createIcons();
  installMixingNav();
  initAiMixingPage();
}

function installMixingNav() {
  const nav = document.querySelector('.nav');
  if (!nav || nav.querySelector('[data-mixing-nav]')) return;
  nav.insertAdjacentHTML('beforeend', `<a data-mixing-nav class="${location.pathname === '/ai-mixing' ? 'active' : ''}" href="/ai-mixing" data-route>${icon('sliders-horizontal')} AI 混音</a>`);
  nav.querySelector('[data-mixing-nav]')?.addEventListener('click', event => { event.preventDefault(); navigate('/ai-mixing'); });
  lucide.createIcons();
}

const originalZhishengNavigate = navigate;
navigate = function(url) {
  if (url === '/ai-mixing') { history.pushState({}, '', url); mountAiMixingPage(); return; }
  originalZhishengNavigate(url);
  setTimeout(() => { initAiMixingPage(); installMixingNav(); }, 0);
};
window.addEventListener('popstate', () => { if (location.pathname === '/ai-mixing') setTimeout(mountAiMixingPage, 0); });
installMixingNav();
if (location.pathname === '/ai-mixing') mountAiMixingPage();

const CHAT_SESSIONS_KEY = 'zhisheng-chat-sessions-v1';
let activeChatId = null;

function readChatSessions() {
  try {
    const stored = JSON.parse(localStorage.getItem(CHAT_SESSIONS_KEY) || '[]');
    return Array.isArray(stored) ? stored : [];
  } catch { return []; }
}

function writeChatSessions(sessions) {
  localStorage.setItem(CHAT_SESSIONS_KEY, JSON.stringify(sessions.slice(0, 30)));
}

function saveCurrentChat() {
  const messages = chatHistory.filter(item => item.role === 'user' || item.role === 'assistant');
  if (!messages.some(item => item.role === 'user')) return;
  const sessions = readChatSessions();
  const firstUser = messages.find(item => item.role === 'user');
  const now = new Date().toISOString();
  if (!activeChatId) {
    activeChatId = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    sessions.unshift({ id: activeChatId, title: firstUser.content.slice(0, 24), messages, updatedAt: now });
  } else {
    const current = sessions.find(item => item.id === activeChatId);
    if (current) {
      current.messages = messages;
      current.updatedAt = now;
      current.title = current.title || firstUser.content.slice(0, 24);
    } else {
      sessions.unshift({ id: activeChatId, title: firstUser.content.slice(0, 24), messages, updatedAt: now });
    }
  }
  writeChatSessions(sessions);
  renderChatSessions();
}

function renderChatMessages() {
  const box = document.querySelector('#messages');
  if (!box) return;
  box.innerHTML = '';
  if (!chatHistory.length) {
    box.innerHTML = `<div class="message"><div class="message-avatar">${icon('sparkles')}</div><div class="bubble">你好，我是智声 AI。告诉我你想制作什么，或描述你的预算、风格和设备需求。</div></div>`;
    lucide.createIcons();
    return;
  }
  chatHistory.forEach(item => appendStreamMessage(item.role === 'user' ? 'user' : 'assistant', item.content));
}

function renderChatSessions() {
  const side = document.querySelector('.chat-side');
  if (!side) return;
  const oldThread = side.querySelector('.thread');
  if (oldThread) oldThread.remove();
  let list = side.querySelector('.thread-list');
  if (!list) {
    list = document.createElement('div');
    list.className = 'thread-list';
    const label = side.querySelector('.side-label');
    if (label) label.after(list);
  }
  const sessions = readChatSessions();
  list.innerHTML = sessions.length ? sessions.map(session => `<button class="thread-item ${session.id === activeChatId ? 'active' : ''}" data-session-id="${session.id}">${escapeChatText(session.title)}</button>`).join('') : '<div class="thread-empty">暂无历史对话</div>';
  list.querySelectorAll('[data-session-id]').forEach(button => button.addEventListener('click', () => {
    const session = readChatSessions().find(item => item.id === button.dataset.sessionId);
    if (!session) return;
    activeChatId = session.id;
    chatHistory.length = 0;
    chatHistory.push(...session.messages);
    renderChatMessages();
    renderChatSessions();
  }));
}

// Final event binding adds persistent local conversation history to the streaming chat.
function bindEvents() {
  document.querySelectorAll('[data-route]').forEach(anchor => anchor.addEventListener('click', event => {
    event.preventDefault();
    navigate(anchor.getAttribute('href'));
  }));
  document.querySelectorAll('[data-play]').forEach(button => button.addEventListener('click', () => {
    const track = button.closest('.track');
    const playing = track.classList.toggle('playing');
    button.innerHTML = icon(playing ? 'pause' : 'play');
    lucide.createIcons();
  }));
  document.querySelectorAll('[data-contact]').forEach(button => button.addEventListener('click', () => navigate('/ai-agent')));
  document.querySelectorAll('.filter').forEach(button => button.addEventListener('click', () => {
    button.parentElement.querySelectorAll('.filter').forEach(item => item.classList.remove('active'));
    button.classList.add('active');
  }));
  document.querySelectorAll('[data-suggest]').forEach(button => button.addEventListener('click', () => {
    const input = document.querySelector('#chatInput');
    if (input) { input.value = button.dataset.suggest; input.focus(); }
  }));
  if (!document.querySelector('#chatForm')) return;
  renderChatSessions();
  renderChatMessages();
  const newChat = document.querySelector('#newChat');
  if (newChat) newChat.addEventListener('click', () => {
    saveCurrentChat();
    activeChatId = null;
    chatHistory.length = 0;
    renderChatMessages();
    renderChatSessions();
    document.querySelector('#chatInput')?.focus();
  });
  const form = document.querySelector('#chatForm');
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const input = document.querySelector('#chatInput');
    const submit = form.querySelector('button[type="submit"]');
    const query = input?.value.trim();
    if (!query || !submit) return;
    input.value = '';
    input.disabled = true;
    submit.disabled = true;
    appendStreamMessage('user', query);
    chatHistory.push({ role: 'user', content: query });
    saveCurrentChat();
    const bubble = appendStreamMessage('assistant');
    try {
      const answer = await streamDeepSeekReply(chatHistory, bubble);
      chatHistory.push({ role: 'assistant', content: answer || '抱歉，我暂时没有生成内容。' });
      if (!answer) bubble.textContent = '抱歉，我暂时没有生成内容。';
      saveCurrentChat();
    } catch (error) {
      bubble.textContent = `连接 AI 失败：${error.message}`;
      chatHistory.pop();
      saveCurrentChat();
    } finally {
      input.disabled = false;
      submit.disabled = false;
      input.focus();
    }
  });
}

// This declaration intentionally replaces the demo-only fake reply handler above.
function bindEvents() {
  document.querySelectorAll('[data-route]').forEach(anchor => anchor.addEventListener('click', event => {
    event.preventDefault();
    navigate(anchor.getAttribute('href'));
  }));
  document.querySelectorAll('[data-play]').forEach(button => button.addEventListener('click', () => {
    const track = button.closest('.track');
    const playing = track.classList.toggle('playing');
    button.innerHTML = icon(playing ? 'pause' : 'play');
    lucide.createIcons();
  }));
  document.querySelectorAll('[data-contact]').forEach(button => button.addEventListener('click', () => navigate('/ai-agent')));
  document.querySelectorAll('.filter').forEach(button => button.addEventListener('click', () => {
    button.parentElement.querySelectorAll('.filter').forEach(item => item.classList.remove('active'));
    button.classList.add('active');
  }));
  document.querySelectorAll('[data-suggest]').forEach(button => button.addEventListener('click', () => {
    const input = document.querySelector('#chatInput');
    if (input) { input.value = button.dataset.suggest; input.focus(); }
  }));
  const newChat = document.querySelector('#newChat');
  if (newChat) newChat.addEventListener('click', () => {
    chatHistory.length = 0;
    const messages = document.querySelector('#messages');
    if (messages) messages.innerHTML = `<div class="message"><div class="message-avatar">${icon('sparkles')}</div><div class="bubble">新的对话已开始。请告诉我你的音频需求。</div></div>`;
    lucide.createIcons();
  });
  const form = document.querySelector('#chatForm');
  if (!form) return;
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const input = document.querySelector('#chatInput');
    const submit = form.querySelector('button[type="submit"]');
    const query = input?.value.trim();
    if (!query || !submit) return;
    input.value = '';
    input.disabled = true;
    submit.disabled = true;
    appendStreamMessage('user', query);
    chatHistory.push({ role: 'user', content: query });
    const bubble = appendStreamMessage('assistant');
    try {
      const answer = await streamDeepSeekReply(chatHistory, bubble);
      chatHistory.push({ role: 'assistant', content: answer || '抱歉，我暂时没有生成内容。' });
      if (!answer) bubble.textContent = '抱歉，我暂时没有生成内容。';
    } catch (error) {
      bubble.textContent = `连接 AI 失败：${error.message}`;
      chatHistory.pop();
    } finally {
      input.disabled = false;
      submit.disabled = false;
      input.focus();
    }
  });
}

// Finish the browser read as soon as DeepSeek emits its terminal [DONE] event.
async function streamDeepSeekReply(messages, bubble) {
  const response = await fetch(CHAT_API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
    body: JSON.stringify({ model: 'deepseek-chat', messages })
  });
  if (!response.ok) {
    let message = `请求失败（${response.status}）`;
    try { message = (await response.json()).error || message; } catch {}
    throw new Error(message);
  }
  if (!response.body) throw new Error('浏览器不支持流式响应');
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let pending = '';
  let answer = '';
  let finished = false;
  while (!finished) {
    const { value, done } = await reader.read();
    pending += decoder.decode(value || new Uint8Array(), { stream: !done });
    const events = pending.split(/\n\n/);
    pending = events.pop() || '';
    for (const event of events) {
      if (/data:\s*\[DONE\]/.test(event)) { finished = true; break; }
      const piece = parseDeepSeekEvent(event);
      if (piece) {
        answer += piece;
        bubble.textContent = answer;
      }
    }
    if (done) break;
  }
  if (!finished && pending) {
    const piece = parseDeepSeekEvent(pending);
    answer += piece;
    bubble.textContent = answer;
  }
  try { await reader.cancel(); } catch {}
  return answer;
}

// The legacy app() call is kept for existing routes; remount this new route after it.
installMixingNav();
if (location.pathname === '/ai-mixing') setTimeout(mountAiMixingPage, 0);

function enhanceHome() {
  const currentPath = location.pathname.replace(/\/$/, '') || '/';
  if (currentPath !== '/' || document.querySelector('.genre-stage')) return;
  const anchor = document.querySelector('.trust-row');
  if (!anchor) return;
  anchor.insertAdjacentHTML('afterend', `
    <section class="shell genre-stage">
      <div class="genre-intro">
        <div><div class="eyebrow">SOUND AESTHETIC</div><h2>每一种风格，都有自己的声场</h2></div>
        <p>从流行旋律的明亮质感，到说唱律动的低频张力，再到古典配器的层次呼吸，为不同创作意图匹配适合的专业资源。</p>
      </div>
      <div class="genre-grid">
        <a class="genre-card pop" href="/arrangement"><div class="genre-content"><span class="genre-index">01 / POP</span><h3>流行音乐</h3><p>旋律、情绪与制作感的平衡，让作品拥有可被记住的第一耳感受。</p></div><span class="card-arrow">${icon('arrow-up-right')}</span></a>
        <a class="genre-card rap" href="/mixing"><div class="genre-content"><span class="genre-index">02 / HIP-HOP</span><h3>说唱音乐</h3><p>强劲的人声表达、清晰咬字与扎实低频，建立作品的态度。</p></div><span class="card-arrow">${icon('arrow-up-right')}</span></a>
        <a class="genre-card classic" href="/arrangement"><div class="genre-content"><span class="genre-index">03 / CLASSICAL</span><h3>古典与影视</h3><p>用动态、空间和配器，为叙事建立更深的声音纵深。</p></div><span class="card-arrow">${icon('arrow-up-right')}</span></a>
      </div>
    </section>`);
  lucide.createIcons();
}

function navigate(url) {
  history.pushState({}, '', url);
  app();
  enhanceHome();
}

window.addEventListener('popstate', () => setTimeout(enhanceHome, 0));
enhanceHome();

// Final binding: keep prior conversations in local storage and restore them on demand.
function bindEvents() {
  document.querySelectorAll('[data-route]').forEach(anchor => anchor.addEventListener('click', event => {
    event.preventDefault();
    navigate(anchor.getAttribute('href'));
  }));
  document.querySelectorAll('[data-play]').forEach(button => button.addEventListener('click', () => {
    const track = button.closest('.track');
    const playing = track.classList.toggle('playing');
    button.innerHTML = icon(playing ? 'pause' : 'play');
    lucide.createIcons();
  }));
  document.querySelectorAll('[data-contact]').forEach(button => button.addEventListener('click', () => navigate('/ai-agent')));
  document.querySelectorAll('.filter').forEach(button => button.addEventListener('click', () => {
    button.parentElement.querySelectorAll('.filter').forEach(item => item.classList.remove('active'));
    button.classList.add('active');
  }));
  document.querySelectorAll('[data-suggest]').forEach(button => button.addEventListener('click', () => {
    const input = document.querySelector('#chatInput');
    if (input) { input.value = button.dataset.suggest; input.focus(); }
  }));
  const form = document.querySelector('#chatForm');
  if (!form) return;
  renderChatSessions();
  renderChatMessages();
  const newChat = document.querySelector('#newChat');
  if (newChat) newChat.addEventListener('click', () => {
    saveCurrentChat();
    activeChatId = null;
    chatHistory.length = 0;
    renderChatMessages();
    renderChatSessions();
    document.querySelector('#chatInput')?.focus();
  });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const input = document.querySelector('#chatInput');
    const submit = form.querySelector('button[type="submit"]');
    const query = input?.value.trim();
    if (!query || !submit) return;
    input.value = '';
    input.disabled = true;
    submit.disabled = true;
    appendStreamMessage('user', query);
    chatHistory.push({ role: 'user', content: query });
    saveCurrentChat();
    const bubble = appendStreamMessage('assistant');
    try {
      const answer = await streamDeepSeekReply(chatHistory, bubble);
      chatHistory.push({ role: 'assistant', content: answer || '抱歉，我暂时没有生成内容。' });
      if (!answer) bubble.textContent = '抱歉，我暂时没有生成内容。';
      saveCurrentChat();
    } catch (error) {
      bubble.textContent = `连接 AI 失败：${error.message}`;
      chatHistory.pop();
      saveCurrentChat();
    } finally {
      input.disabled = false;
      submit.disabled = false;
      input.focus();
    }
  });
}

app();
enhanceHome();

// DeepSeek may use CRLF between SSE events; accept either CRLF or LF boundaries.
async function streamDeepSeekReply(messages, bubble) {
  const response = await fetch(CHAT_API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
    body: JSON.stringify({ model: 'deepseek-chat', messages })
  });
  if (!response.ok) {
    let message = `请求失败（${response.status}）`;
    try { message = (await response.json()).error || message; } catch {}
    throw new Error(message);
  }
  if (!response.body) throw new Error('浏览器不支持流式响应');
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let pending = '';
  let answer = '';
  let finished = false;
  while (!finished) {
    const { value, done } = await reader.read();
    pending += decoder.decode(value || new Uint8Array(), { stream: !done });
    const events = pending.split(/\r?\n\r?\n/);
    pending = events.pop() || '';
    for (const event of events) {
      if (/data:\s*\[DONE\]/.test(event)) { finished = true; break; }
      const piece = parseDeepSeekEvent(event);
      if (piece) {
        answer += piece;
        bubble.textContent = answer;
      }
    }
    if (done) break;
  }
  if (!finished && pending) {
    const piece = parseDeepSeekEvent(pending);
    answer += piece;
    bubble.textContent = answer;
  }
  try { await reader.cancel(); } catch {}
  return answer;
}
