/**
 * 精致81x81 Tabbar图标 - 高保真版
 * 线性(未选中): #888888 统一2px纤细描边
 * 实心(选中): #3A3A3A 填充
 * 图标: 简约房子/规整网格/极简气泡/简洁购物车/柔和用户轮廓
 */
const fs = require('fs')
const path = require('path')
const zlib = require('zlib')

const S = 81
const LIN = [0x88, 0x88, 0x88, 0xFF]
const FIL = [0x3A, 0x3A, 0x3A, 0xFF]
const BG  = [0, 0, 0, 0]
const SW  = 2

// ======== PNG编码器 ========
function crc32(b){let c=0xFFFFFFFF;const t=new Int32Array(256);for(let i=0;i<256;i++){let x=i;for(let j=0;j<8;j++)x=(x&1)?0xEDB88320^(x>>>1):(x>>>1);t[i]=x}for(let i=0;i<b.length;i++)c=t[(c^b[i])&0xFF]^(c>>>8);return(c^0xFFFFFFFF)>>>0}
function chunk(tp,d){const t=Buffer.from(tp,'ascii'),l=Buffer.alloc(4);l.writeUInt32BE(d.length);const c=Buffer.alloc(4);c.writeUInt32BE(crc32(Buffer.concat([t,d])));return Buffer.concat([l,t,d,c])}
function toPNG(cv){const w=cv.w,h=cv.h;const raw=Buffer.alloc(h*(1+w*4));for(let y=0;y<h;y++){raw[y*(1+w*4)]=0;for(let x=0;x<w;x++){const p=cv.px[y*w+x],o=y*(1+w*4)+1+x*4;raw[o]=p[0];raw[o+1]=p[1];raw[o+2]=p[2];raw[o+3]=p[3]}}const z=zlib.deflateSync(raw,{level:9});const sig=Buffer.from([137,80,78,71,13,10,26,10]);const ih=Buffer.alloc(13);ih.writeUInt32BE(w,0);ih.writeUInt32BE(h,4);ih[8]=8;ih[9]=6;return Buffer.concat([sig,chunk('IHDR',ih),chunk('IDAT',z),chunk('IEND',Buffer.alloc(0))])}

// ======== 画布与基础图形 ========
function C(w,h){const px=new Array(w*h).fill(null).map(()=>[...BG]);return{w,h,px}}
function sp(cv,x,y,c){x=Math.round(x);y=Math.round(y);if(x>=0&&x<cv.w&&y>=0&&y<cv.h)cv.px[y*cv.w+x]=[...c]}
function fr(cv,x1,y1,x2,y2,c){for(let y=y1;y<=y2;y++)for(let x=x1;x<=x2;x++)sp(cv,x,y,c)}
function fc(cv,cx,cy,r,c){for(let y=-r;y<=r;y++)for(let x=-r;x<=r;x++)if(x*x+y*y<=r*r)sp(cv,cx+x,cy+y,c)}
function sc(cv,cx,cy,r,c,t){t=t||SW;for(let y=-r-t;y<=r+t;y++)for(let x=-r-t;x<=r+t;x++){const d=Math.sqrt(x*x+y*y);if(d>=r-t/2&&d<=r+t/2)sp(cv,cx+x,cy+y,c)}}
function sl(cv,x1,y1,x2,y2,c,t){t=t||SW;const dx=x2-x1,dy=y2-y1,len=Math.sqrt(dx*dx+dy*dy),st=Math.max(Math.ceil(len),1);for(let i=0;i<=st;i++){const tt=i/st,x=Math.round(x1+dx*tt),y=Math.round(y1+dy*tt);for(let ty=-t/2;ty<t/2;ty++)for(let tx=-t/2;tx<t/2;tx++)sp(cv,x+tx,y+ty,c)}}
function ft(cv,x1,y1,x2,y2,x3,y3,c){const my=Math.min(y1,y2,y3),My=Math.max(y1,y2,y3);for(let y=my;y<=My;y++){const xs=[];const ps=[[x1,y1],[x2,y2],[x3,y3]];for(let i=0;i<3;i++){const[a,b]=ps[i],[d,e]=ps[(i+1)%3];if((b<=y&&e>y)||(e<=y&&b>y))xs.push(a+(y-b)/(e-b)*(d-a))}if(xs.length>=2){xs.sort((a,b)=>a-b);for(let x=Math.round(xs[0]);x<=Math.round(xs[1]);x++)sp(cv,x,y,c)}}}
function frr(cv,x1,y1,x2,y2,r,c){fr(cv,x1+r,y1,x2-r,y2,c);fr(cv,x1,y1+r,x2,y2-r,c);fc(cv,x1+r,y1+r,r,c);fc(cv,x2-r,y1+r,r,c);fc(cv,x1+r,y2-r,r,c);fc(cv,x2-r,y2-r,r,c)}
function srr(cv,x1,y1,x2,y2,r,c,t){t=t||SW;sl(cv,x1+r,y1,x2-r,y1,c,t);sl(cv,x1+r,y2,x2-r,y2,c,t);sl(cv,x1,y1+r,x1,y2-r,c,t);sl(cv,x2,y1+r,x2,y2-r,c,t);sc(cv,x1+r,y1+r,r,c,t);sc(cv,x2-r,y1+r,r,c,t);sc(cv,x1+r,y2-r,r,c,t);sc(cv,x2-r,y2-r,r,c,t)}

// ======== 图标绘制(优化比例) ========

// 1. 简约房子 - 宽体三角屋顶+方正墙体+门洞
function drawHome(cv, c, fill) {
  const cx=40, roofTop=13, wallTop=36, wallBot=67, wallL=17, wallR=63
  if(fill){
    ft(cv,cx,roofTop,wallL-1,wallTop,wallR+1,wallTop,c)
    fr(cv,wallL,wallTop,wallR,wallBot,c)
    fr(cv,34,52,46,wallBot,BG)
    fr(cv,34,52,46,52,c)
  } else {
    sl(cv,cx,roofTop,wallL-1,wallTop,c,SW)
    sl(cv,cx,roofTop,wallR+1,wallTop,c,SW)
    sl(cv,wallL-1,wallTop,wallR+1,wallTop,c,SW)
    sl(cv,wallL,wallTop,wallL,wallBot,c,SW)
    sl(cv,wallR,wallTop,wallR,wallBot,c,SW)
    sl(cv,wallL,wallBot,wallR,wallBot,c,SW)
    sl(cv,34,52,34,wallBot,c,SW)
    sl(cv,46,52,46,wallBot,c,SW)
    sl(cv,34,52,46,52,c,SW)
  }
}

// 2. 规整网格 - 2x2大方块(更规整清晰)
function drawGrid(cv, c, fill) {
  const s=18, gap=8, tw=2*s+gap
  const ox=Math.round((81-tw)/2), oy=Math.round((81-tw)/2)
  for(let r=0;r<2;r++)for(let col=0;col<2;col++){
    const x=ox+col*(s+gap), y=oy+r*(s+gap)
    if(fill) frr(cv,x,y,x+s-1,y+s-1,3,c)
    else srr(cv,x,y,x+s-1,y+s-1,3,c,SW)
  }
}

// 3. 极简消息气泡 - 圆角矩形+左下尾巴+三点
function drawChat(cv, c, fill) {
  const x1=14,y1=14,x2=66,y2=50,r=8
  if(fill){
    frr(cv,x1,y1,x2,y2,r,c)
    ft(cv,24,y2,38,y2,20,65,c)
    // 三点
    fc(cv,30,30,2,c);fc(cv,40,30,2,c);fc(cv,50,30,2,c)
  } else {
    srr(cv,x1,y1,x2,y2,r,c,SW)
    sl(cv,24,y2,20,65,c,SW)
    sl(cv,38,y2,20,65,c,SW)
    // 三点
    fc(cv,30,30,2,c);fc(cv,40,30,2,c);fc(cv,50,30,2,c)
  }
}

// 4. 简洁购物小车 - 扶手+梯形车体+双轮
function drawCart(cv, c, fill) {
  if(fill){
    fr(cv,10,17,24,19,c)
    sl(cv,24,17,28,33,c,3)
    fr(cv,28,33,68,49,c)
    fr(cv,26,37,28,49,c)
    fr(cv,68,29,70,49,c)
    fr(cv,28,29,70,33,c)
    fc(cv,36,59,5,c);fc(cv,60,59,5,c)
  } else {
    sl(cv,10,17,24,17,c,SW)
    sl(cv,24,17,28,33,c,SW)
    sl(cv,28,33,70,29,c,SW)
    sl(cv,28,33,26,49,c,SW)
    sl(cv,26,49,68,49,c,SW)
    sl(cv,68,49,70,29,c,SW)
    sc(cv,36,59,5,c,SW)
    sc(cv,60,59,5,c,SW)
  }
}

// 5. 柔和用户轮廓 - 圆形头部+圆弧肩部
function drawUser(cv, c, fill) {
  const hcx=40,hcy=25,hr=12
  const btop=47,bbot=66,bleft=18,bright=62,br=10
  if(fill){
    fc(cv,hcx,hcy,hr,c)
    frr(cv,bleft,btop,bright,bbot,br,c)
  } else {
    sc(cv,hcx,hcy,hr,c,SW)
    // 左侧
    sl(cv,bleft,bbot-br,bleft,btop+br,c,SW)
    sc(cv,bleft+br,btop+br,br,c,SW)
    // 顶部
    sl(cv,bleft+br,btop,bright-br,btop,c,SW)
    // 右侧
    sc(cv,bright-br,btop+br,br,c,SW)
    sl(cv,bright,btop+br,bright,bbot-br,c,SW)
    // 底部
    sl(cv,bleft,bbot,bright,bbot,c,SW)
  }
}

// ======== 生成 ========
const dir = path.join(__dirname, 'assets')
const icons = [
  {n:'tab-home',d:drawHome},{n:'tab-category',d:drawGrid},
  {n:'tab-service',d:drawChat},{n:'tab-cart',d:drawCart},{n:'tab-user',d:drawUser}
]
icons.forEach(({n,d})=>{
  const lc=C(S,S);d(lc,LIN,false);fs.writeFileSync(path.join(dir,n+'.png'),toPNG(lc));console.log(n+'.png')
  const fc2=C(S,S);d(fc2,FIL,true);fs.writeFileSync(path.join(dir,n+'-active.png'),toPNG(fc2));console.log(n+'-active.png')
})
console.log('Done! 10 icons generated.')