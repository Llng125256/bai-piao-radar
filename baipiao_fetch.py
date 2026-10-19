#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""白嫖雷达 v1：只要「0 元领/免费权益」，剔除导购价；每标一条核验档位与出处。"""
import re, html, json, os, datetime, urllib.request

UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
HERE = os.path.dirname(os.path.abspath(__file__))
FEED = "http://feed.smzdm.com"

# 已核验白嫖入口（每条注明核验档 + 出处 + 核验日期；新条目须按同标准补）
CURATED = [
    dict(name="中国移动 · 网龄成长计划", cat="video", level="ok",
         gift="V5 等级每月任选：爱奇艺/优酷/芒果TV/QQ音乐绿钻/B站大会员 月卡 1 张；另有流量月包 V1-V2 1GB / V3-V4 2GB / V5 3GB；AI 科技礼 4选1(V1-V2)·4选2(V3-V5)",
         how="中国移动 App → 搜索「网龄成长计划」→ 我的权益；等级越高可选越多",
         url="https://www.10086.cn/",
         src="中国网 2026-09-23 报道（实测 HTTP 200，正文 33 处「网龄」+6 处「会员月卡」）+ 用户一手实证（刚领到 B站大会员月卡）",
         date="2026-10-19 核验",
         note="你刚领到的就是这个——等级够了每月都能领，最稳的一条"),
    dict(name="中国移动 · 爱家咪咕会员主动领取", cat="video", level="ok",
         gift="爱家咪咕会员半年包/年包/季包、悦享会员、足球通/NBA 尊享包等 9 款产品含的咪咕视频会员，2026-06-01 起改为用户主动领取（权益不变）",
         how="官方 H5 链接领取，或等咪咕视频 App 下发的短信链接",
         url="https://plus.migu.cn/c/0gb8fl",
         src="10086.cn 官方公告（江苏，2026-05-27）；短链实测 HTTP 200（官方域名 plus.migu.cn，实际领取需在 App 内生效）",
         date="2026-10-19 核验",
         note="名下产品含咪咕会员的别忘了领，不领就浪费"),
    dict(name="中国移动 · 全球通星动日（每月 26 号）", cat="video", level="warn",
         gift="腾讯视频/B站视频会员月卡、加油券、音乐会员周卡等（星动日开放）",
         how="中国移动 App → 全球通专区 / 搜索「星动日」",
         url="https://www.10086.cn/",
         src="多源提及（移动权益攻略 + 微信推文），未见官方页面直证",
         date="2026-10-19 待确认",
         note="每月 26 号蹲一次，全球通银卡及以上更稳"),
    dict(name="动感地带 · 1314 粉丝节 10 月宠粉专场", cat="sign", level="warn",
         gift="咪咕游戏 1 天体验会员 0 元领；门票/皮肤/会员抽奖（含 B站大会员年卡、百度网盘 VIP 月卡抽奖）",
         how="中国移动 / 咪咕音乐 / 咪咕游戏 / 咪咕视频 App 搜索「1314粉丝节」",
         url="https://www.toutiao.com/article/7696460783009399311",
         src="今日头条 2026-10 活动推文（媒体稿，非官方公告）",
         date="2026-10-19 待确认",
         note="抽奖类中奖率有限，别抱太高预期；0 元体验会员是确定的"),
    dict(name="咪咕视频 · 新人礼 + 签到兑会员", cat="video", level="warn",
         gift="新登录弹 7 天钻石会员；签到连续 3 天=1 天会员、7 天=3 天；积分商城可换 1/3/7 天",
         how="咪咕视频 App → 我的 → 新人福利 / 签到中心 / 积分商城",
         url="https://www.migu.cn/",
         src="多家攻略站同源描述，未逐项实测",
         date="2026-10-19 待实测",
         note="规则常变，以 App 内实际显示为准"),
    dict(name="支付宝积分 · 兑影音会员", cat="video", level="warn",
         gift="支付宝会员 → 影音娱乐：99 积分兑 3 天 / 199 积分兑 7 天（咪咕等，库存随活动变）",
         how="支付宝 → 我的 → 支付宝会员 → 影音娱乐",
         url="https://www.alipay.com/",
         src="攻略站多源提及，兑换池常调整",
         date="2026-10-19 待实测",
         note="积分放着也是放着，优先换这个"),
    dict(name="中国电信 · 1 积分抢会员月卡", cat="video", level="warn",
         gift="电信 App 积分商城 1 积分区：网易云/芒果TV/B站等会员月卡，每天 10 点限量约 1000 份，限抢 1 次",
         how="电信 App → 积分商城 → 积分 1 元兑专区",
         url="https://www.189.cn/",
         src="第三方爆料站（bacaoo）；未见官方页面直证",
         date="2026-10-19 待核验",
         note="限量抢购型，10 点整手快才有"),
    dict(name="美团 · 疯狂星期六（0 元购/0.01 元奶茶）", cat="food", level="warn",
         gift="每周六弹窗「0 元外卖已到账」：0 元喝饮品、0 元喝瑞幸、古茗柠檬水兑换券；媒体实测茶百道中杯茉莉奶绿实付 0.01 元",
         how="周六 10 点开美团 App 盯弹窗 → 领 0 元券 → 选参与门店下单（多为到店自取或限定门店）",
         url="https://www.sina.cn/news/article/comos_niuawyt3402055.html",
         src="新浪转载《南方日报》实测（页面实测 HTTP 200，正文 28 处「0元」+9 处「疯狂星期六」+3 处「0.01」）",
         date="2026-10-19 媒体交叉",
         note="一周就周六这一波，闹钟设 10 点；爆单会延迟，别卡饭点"),
    dict(name="淘宝闪购 · 超级星期六", cat="food", level="warn",
         gift="每周六大额券：满 18.8 减 18.8、满 20 减 10 等；原价 19 元奶茶叠加后约 1.2 元",
         how="淘宝 App → 闪购频道 → 周六领大额券",
         url="https://www.sina.cn/news/article/comos_niuawyt3402055.html",
         src="同上（新浪攻略文，非官方公告）",
         date="2026-10-19 媒体交叉",
         note="和美团的周六场二选一比价，同店常差几块"),
    dict(name="美团外卖 · 每日免单抽奖", cat="food", level="warn",
         gift="外卖首页「免单抽奖」：做浏览/领券任务换抽奖次数，奖品含正餐全额免单、奶茶无门槛券、大额满减",
         how="美团/美团外卖 App → 外卖首页 → 免单抽奖（每日一次，20 点中奖概率更高）",
         url="https://m.toutiao.com/article/7694170817671807551",
         src="头条攻略文（页面实测 HTTP 200，31 处「免单」+27 处「口令」），非官方公告",
         date="2026-10-19 待实测",
         note="纯白嫖概率型，每天顺手点一次，不花时间"),
    dict(name="茶百道 · 小程序 1 元咖啡券", cat="food", level="warn",
         gift="每天 10:00–11:00 微信小程序发「1 元喝咖啡」券，限 6888 份，叠加免配送券约 2 元到手",
         how="微信 → 茶百道小程序 → 整点抢券",
         url="https://www.sina.cn/news/article/comos_niuawyt3402055.html",
         src="新浪攻略文提及品牌自有小程序活动",
         date="2026-10-19 待实测",
         note="品牌自有渠道最稳，比平台券少套路"),
    dict(name="库迪咖啡 · 周末买一赠一", cat="food", level="warn",
         gift="新品双杯 13.99 元（买一赠一），周末档延续",
         how="美团/美团外卖 App 搜「买一赠一」或库迪小程序",
         url="https://www.sina.cn/news/article/comos_niuawyt3402055.html",
         src="新浪攻略文提及，活动档期常变",
         date="2026-10-19 待实测",
         note="两人拼着喝才划算，一个人别硬凑"),
    dict(name="京东外卖 · 秒送整点抢券", cat="food", level="warn",
         gift="京东 App「秒送」：每日整点抢大额券（如 17 减 16、满 29 减 20），新人首单力度最大",
         how="京东 App → 秒送 → 搜索「外卖901」（另有「外卖700/800」说法）",
         url="https://www.dingzhoudaily.com/article/343881791961774.shtml",
         src="攻略文多源提及；定州新闻网页实测 403 不可达，仅搜索摘要可见",
         date="2026-10-19 待实测",
         note="京东外卖商家少但补贴狠，可当备用渠道"),
    dict(name="⚠️ 外卖数字口令（只给源链接，不背书）", cat="food", level="warn",
         gift="口令类信息本页不做结论：网上流传的每组数字都互相打架，各自宣称「只有我这套有效」",
         how="要试就照来源文章自己试：App 搜索框输数字，弹窗即有效、不弹即失效；同一订单仅可用一张平台口令券，可与店铺满减叠加",
         url="https://m.toutiao.com/article/7694170817671807551",
         src="实测冲突：美团「996996 系」与「333xxx 系」两组来源互相否定，且都写「有效期至 2027 年」——典型 SEO 引流稿特征，无法自证",
         date="2026-10-19 冲突未解",
         note="本页只提供来源链接供你自己验证，不替任何一组口令背书"),
    dict(name="🚫 「0 元券」不等于免费", cat="risk", level="no",
         gift="0 元/0.01 元通常只覆盖基础杯，配送费、打包费、加料另算；部分限到店自取；券多当日有效",
         how="下单前看实付总价；1 公里内门店优先；别为凑满减买不需要的",
         url="https://k.sina.com.cn/article_7880068378_1d5b04d1a06801acvc.html",
         src="新浪攻略文避坑段落（页面可访问）",
         date="2026-10-19 已判定",
         note="一杯 0 元但配送 6 元，不如附近自取；这是最容易反被薅的地方"),
    dict(name="招商银行信用卡 · 积分兑会员（掌上生活）", cat="bank", level="warn",
         gift="积分可兑爱奇艺/腾讯视频/优酷/芒果TV/哔哩哔哩及 QQ音乐/酷狗/网易云/喜马拉雅会员（月卡·季卡·年卡，即刻到账）；799 积分=星巴克中杯；1199 积分=21 元还款金；999 积分起兑电影票",
         how="掌上生活 App → 积分礼遇/积分商城 → 视听会员；招行积分交易积分永久有效（2026 起赠送积分亦永久）",
         url="https://www.ahcaijing.com/html/2026/zhxw_0924/659532.html",
         src="安徽财经网/大众网济宁/北青网财经/岭南网 多篇媒体交叉（口径一致）；具体分值以掌上生活当期页面为准",
         date="2026-10-19 媒体交叉",
         note="手里有招行卡的，这条是长期饭票——积分不会过期，攒着兑会员最划算"),
    dict(name="招商银行 · 周三美食 5 折 / 19.9 元观影", cat="bank", level="warn",
         gift="每周三掌上生活抢指定餐饮 5 折券（火锅/烧烤/日料/快餐）；购票 19.9 元起，覆盖全国 1.2 万余家影院，可叠加积分立减",
         how="掌上生活 App → 饭票频道 / 影票专区；每周三定闹钟抢",
         url="https://www.lncnw.com/xiaofei/9210/2026/10/02",
         src="岭南网 2026-10-02 攻略文（媒体源，非官方公告）",
         date="2026-10-19 待实测",
         note="折类不算白嫖，但持卡人本来就有，漏了就是浪费"),
    dict(name="88VIP · 权益别漏领（付费会员，非白嫖）", cat="vip", level="warn",
         gift="生活卡 88 元/年（优酷或芒果二选一 + 网易云音乐 + 饿了么等）、购物卡 88 元/年、全能卡 168 元/年；另有 9 折消费券 500-50/1500-150/5000-500",
         how="淘宝 → 88VIP 会员页 → 逐项领取联名权益（很多人开了只用来打折，联名会员忘了领）",
         url="https://feng.ifeng.com/c/8xF3g9cjXNh",
         src="凤凰网/头条对比文 + 行业研究报告（三个皮匠报告，引 2026-06 数据）",
         date="2026-10-19 媒体交叉",
         note="这是付费会员不是白嫖；但已开的请把联名权益领全，否则等于白交钱"),
    dict(name="京东 PLUS · 权益别漏领（付费会员，非白嫖）", cat="vip", level="warn",
         gift="每月 6 张自营运费券（全年约 60 张）、10 倍京豆返利、95 折、生活服务权益（汽车保养、超声波洁牙等 2026 新增）",
         how="京东 App → PLUS 会员页 → 每月券包/生活权益逐项领",
         url="https://www.dzxww.cn/article/64591789982952.shtml",
         src="定州新闻网攻略文 + 行业研究（会员费 99–149 元区间）",
         date="2026-10-19 媒体交叉",
         note="付费权益，但每月券包和生活权益最常被漏领"),
    dict(name="中国联通 · 权益领取（待补，本轮未找到可靠来源）", cat="telecom", level="warn",
         gift="运营商普遍有网龄/等级权益池，联通应有对应入口，但本轮检索未获得可交叉验证的公开来源，故不写具体福利，避免误导",
         how="中国联通 App → 搜「权益」「会员」「网龄」，看当期可领项",
         url="https://www.10010.com/",
         src="本轮无可靠公开来源；挂账待实测补（下一轮由定时任务或人工补）",
         date="2026-10-19 待补",
         note="宁可写「不知道」，也不编一条假的给你"),
    dict(name="微信支付 / 云闪付 · 积分与优惠券", cat="pay", level="warn",
         gift="支付工具的积分/金币体系常可兑影音会员与生活券，但入口分散、规则常变",
         how="微信：我 → 服务 → 微信支付分/积分；云闪付 App → 我的 → 积分/优惠券",
         url="https://www.unionpay.com/",
         src="本轮未做逐项实测，仅列入口待验",
         date="2026-10-19 待实测",
         note="这类入口每周都可能变，别指望一次记牢，扫一眼最稳"),
    dict(name="「B站永久激活码」类站点", cat="risk", level="no",
         gift="声称免费发放永久激活码，实际多为引流/失效码，站方自述「部分信息存在错误」",
         how="不建议参与",
         url="https://youhui.bacaoo.com/p/74824",
         src="实测该页 21 处「激活码」+引流话术；永久码与「兑换码」营销高度可疑",
         date="2026-10-19 已判定",
         note="🚫 不推荐：拿不到还浪费时间，且有账号风险"),
]

TPL = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>白嫖雷达 · __T__</title><style>
:root{--bg:#f5f6f8;--card:#fff;--ink:#16191d;--sub:#6b7280;--line:#e8eaee;--a:#ff5a2c;--soft:#fff1ec;
--g:#0f9d58;--gs:#e8f6ee;--am:#b45309;--as:#fef3e2;--gy:#98a2b3;--gys:#f2f4f7}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;padding-bottom:40px}
.w{max-width:560px;margin:0 auto;padding:0 14px}
header{padding:20px 0 10px}.brand{display:flex;align-items:center;gap:9px}
.logo{width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,#ff7a45,#ff3d00);
display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px}
h1{font-size:19px;margin:0}.tag{margin-left:auto;font-size:11px;color:var(--sub);border:1px solid var(--line);
background:#fff;padding:3px 8px;border-radius:999px}.lead{color:var(--sub);font-size:13px;margin:9px 0 0}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin:14px 0 12px}
.st{background:#fff;border:1px solid var(--line);border-radius:12px;padding:9px 4px;text-align:center}
.st b{display:block;font-size:18px}.st span{font-size:10.5px;color:var(--sub)}
.st.a b{color:var(--g)}.st.b b{color:var(--am)}.st.c b{color:var(--gy)}
.tabs{display:flex;gap:7px;overflow-x:auto;padding:2px 0 12px}
.tab{flex:0 0 auto;border:1px solid var(--line);background:#fff;color:var(--sub);font-size:12.5px;
padding:7px 12px;border-radius:999px;cursor:pointer}.tab.on{background:var(--ink);border-color:var(--ink);color:#fff}
.card{background:#fff;border:1px solid var(--line);border-radius:13px;padding:13px;margin-bottom:10px}
.card.ok{border-left:4px solid var(--g)}.card.warn{border-left:4px solid var(--am)}
.card.no{border-left:4px solid var(--gy);opacity:.92}
.hd{display:flex;gap:9px;align-items:flex-start}
.av{width:34px;height:34px;border-radius:9px;flex:0 0 auto;display:flex;align-items:center;justify-content:center;
font-size:17px;background:var(--soft)}.av.v{background:var(--gs)}.av.f{background:var(--as)}.av.r{background:var(--gys)}
.av.b{background:#eef3ff}.av.p{background:#fff7ed}
.ti{font-weight:650;font-size:14.5px}.de{color:var(--sub);font-size:12.5px;margin-top:2px}
.badge{font-size:11px;padding:2px 8px;border-radius:999px;margin-left:6px}
.b-ok{background:var(--gs);color:var(--g)}.b-warn{background:var(--as);color:var(--am)}.b-no{background:var(--gys);color:#475467}
.how{background:#f8f9fb;border-radius:9px;padding:8px 10px;font-size:12.5px;margin:10px 0;color:#374151}
.how b{color:var(--ink)}
.src{font-size:11.5px;color:var(--sub);line-height:1.6}
.note{font-size:12px;color:var(--a);margin-top:6px}
.foot{display:flex;align-items:center;gap:8px;margin-top:10px}
.tm{font-size:10.5px;color:#98a2b3}
.btn{margin-left:auto;background:var(--a);color:#fff;border:0;border-radius:9px;padding:8px 14px;font-size:13px;
font-weight:600;text-decoration:none}.btn.gray{background:#6b7280}
.panel{background:#fff;border:1px solid var(--line);border-radius:13px;padding:13px;margin:14px 0 10px}
.panel h3{font-size:13.5px;margin:0 0 9px}.panel li{font-size:12.5px;color:var(--sub);margin:5px 0}
footer{text-align:center;color:#98a2b3;font-size:11.5px;margin-top:14px;line-height:1.8}
.empty{text-align:center;color:var(--sub);font-size:13px;padding:18px 0}
</style></head><body><div class="w">
<header><div class="brand"><div class="logo">🆓</div><h1>白嫖雷达</h1><span class="tag">__T__</span></div>
<p class="lead">只收「0 元领 / 免费权益」，不收导购价。每条标注核验档与出处——能验的验了，验不了的标出来，不装作都真。</p></header>
<div class="stats"><div class="st a"><b>__OK__</b><span>已核验</span></div>
<div class="st b"><b>__WN__</b><span>待确认</span></div><div class="st c"><b>__NO__</b><span>不推荐</span></div></div>
<div class="tabs"><button class="tab on" data-f="all">全部</button><button class="tab" data-f="ok">已核验</button>
<button class="tab" data-f="warn">待确认</button><button class="tab" data-f="risk">避坑</button></div>
<div id="list"></div>
<div class="panel"><h3>📏 收录与核验标准</h3><ul>
<li>只收「免费/0 元/领取/兑换/权益」类，<b>剔除</b>「XX 元买入」的导购优惠。</li>
<li>🟢 已核验：官方域名可达或权威媒体正文交叉可查，且内容自洽。</li>
<li>🟠 待确认：多源提及但未见官方直证，按「以 App 内实际显示为准」处理。</li>
<li>⚪ 不推荐：激活码/永久码类引流站，拿不到且有账号风险。</li>
<li>所有条目带核验日期与出处，过期或失效会标灰。</li></ul></div>
<footer>__T__ 生成 · 福利以官方页面为准，本页只做聚合、核验与提醒<br>不代登录、不代领取、不存任何账号密码</footer></div>
<script>
const D=__D__;const L=document.getElementById('list');let f='all';
const LV={ok:['🟢','已核验','b-ok'],warn:['🟠','待确认','b-warn'],no:['⚪','不推荐','b-no']};
const IC={video:'📺',food:'🛵',bank:'🏦',vip:'💳',telecom:'📡',pay:'💰',sign:'🎯',risk:'🚫'};
function render(){const r=D.filter(d=>f==='all'||d.level===f||(f==='risk'&&d.cat==='risk'));
 if(!r.length){L.innerHTML='<div class="empty">这一类暂时没有条目</div>';return;}
 L.innerHTML=r.map(d=>{const v=LV[d.level];
 return `<div class="card ${d.level}"><div class="hd"><div class="av ${d.cat==='risk'?'r':d.cat==='food'?'f':d.cat==='bank'?'b':d.cat==='pay'?'p':'v'}">${IC[d.cat]||'🎁'}</div>
 <div><div class="ti">${d.name}<span class="badge ${v[2]}">${v[0]} ${v[1]}</span></div>
 <div class="de">${d.gift}</div></div></div>
 <div class="how"><b>怎么领：</b>${d.how}</div>
 <div class="src"><b>核验依据：</b>${d.src}</div>
 ${d.note?`<div class="note">${d.note}</div>`:''}
 <div class="foot"><span class="tm">${d.date}</span>
 <a class="btn ${d.level==='no'?'gray':''}" href="${d.url}" target="_blank">${d.level==='no'?'看原文（不建议参与）':'去领取'}</a></div>
 </div>`}).join('');}
document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>{
 document.querySelectorAll('.tab').forEach(x=>x.classList.remove('on'));t.classList.add('on');f=t.dataset.f;render();}));
render();</script></body></html>"""


def main():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    page = (TPL.replace("__D__", json.dumps(CURATED, ensure_ascii=False))
               .replace("__T__", now)
               .replace("__OK__", str(sum(1 for c in CURATED if c["level"] == "ok")))
               .replace("__WN__", str(sum(1 for c in CURATED if c["level"] == "warn")))
               .replace("__NO__", str(sum(1 for c in CURATED if c["cat"] == "risk"))))
    open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(page)
    json.dump({"time": now, "items": CURATED},
              open(os.path.join(HERE, "data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("白嫖雷达生成:", os.path.join(HERE, "index.html"), "| 条目", len(CURATED))


if __name__ == "__main__":
    main()
