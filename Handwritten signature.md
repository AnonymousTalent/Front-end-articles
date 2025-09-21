# 用canvas实现手写签名功能
最近开发网站有一个需求，要求页面上有一块区域，用户能用鼠标在上面写字，并能保存成图片 base64 码放在服务器。
这样的需求用 canvas 实现是最好的。
需要用到 canvas 的以下几个属性：

  * beginPath 创建一个新的路径
  * globalAlpha 设置图形和图片透明度的属性
  * lineWidth 设置线段厚度的属性（即线段的宽度）
  * strokeStyle 描述画笔（绘制图形）颜色或者样式的属性，默认值是 #000 (black)
  * moveTo(x, y)  将一个新的子路径的起始点移动到(x，y)坐标的方法
  * lineTo(x, y) 使用直线连接子路径的终点到x，y坐标的方法（并不会真正地绘制）
  * closePath 它尝试从当前点到起始点绘制一条直线
  * stroke 它会实际地绘制出通过 moveTo() 和 lineTo() 方法定义的路径，默认颜色是黑色

除了用到这些属性外，还需要监听鼠标点击和鼠标移动事件。

之前链接的外部代码示例存在一个微妙的内存泄漏问题：如果在画布上按下鼠标后，将鼠标移出浏览器窗口再松开，会导致`mousemove`事件监听器无法被移除，从而阻止了画布元素被垃圾回收。

下面是一个修复了该问题的完整代码示例。它通过使用具名函数和`window`对象上的`addEventListener`/`removeEventListener`，确保所有事件监听器在鼠标松开时（无论在何处松开）都能被正确清理。

### 完整代码示例

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Canvas Signature Pad (Leak-Free Example)</title>
    <style>
        body { font-family: sans-serif; }
        canvas { border: 1px solid #ccc; }
        .controls { margin-bottom: 10px; }
        .sub-controls { display: none; margin-top: 5px; }
    </style>
</head>
<body>

    <h2>Canvas Signature Pad</h2>

    <div class="controls">
        <input type="radio" name="tool" id="huabi" value="huabi" checked><label for="huabi">画笔 (Pen)</label>
        <input type="radio" name="tool" id="shuazi" value="shuazi"><label for="shuazi">刷子 (Brush)</label>
        <input type="radio" name="tool" id="penqiang" value="penqiang"><label for="penqiang">喷枪 (Spray)</label>
        <input type="radio" name="tool" id="xiangpi" value="xiangpi"><label for="xiangpi">橡皮 (Eraser)</label>

        <div class="sub-controls">
            <label>Shape:</label>
            <select id="eraser-shape">
                <option value="rect">Rect</option>
                <option value="circle">Circle</option>
            </select>
            <label>Size (px):</label>
            <input value="10" id="eraser-size" type="number">
        </div>
    </div>

    <canvas id="signature-canvas" width="800" height="600"></canvas>

    <script>
(function() {
    // Helper to select elements
    function $(selector) {
        return document.querySelector(selector);
    }

    // --- State Variables ---
    let tool = 'huabi';
    let eraserShape = 'rect';
    let eraserSize = 10;
    let drawing = false;
    let lastX = 0;
    let lastY = 0;

    // --- DOM Elements ---
    const canvas = $('#signature-canvas');
    const ctx = canvas.getContext('2d');
    const controls = $('.controls');
    const subControls = $('.sub-controls');

    // --- Event Handlers ---

    // Handles tool selection
    controls.addEventListener('change', (event) => {
        if (event.target.name === 'tool') {
            tool = event.target.value;
            subControls.style.display = (tool === 'xiangpi') ? 'block' : 'none';
        }
    });

    // Handles eraser shape and size changes
    $('#eraser-shape').addEventListener('change', (e) => eraserShape = e.target.value);
    $('#eraser-size').addEventListener('input', (e) => eraserSize = e.target.value);

    // --- Robust Mouse Event Handling to Prevent Leaks ---

    function handleMouseDown(event) {
        drawing = true;
        // Get coordinates relative to the canvas
        [lastX, lastY] = [event.offsetX, event.offsetY];

        // Attach listeners to the window to capture events everywhere
        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('mouseup', handleMouseUp);
        // Also listen for mouseleave to prevent leaks if mouse is released outside window
        window.addEventListener('mouseleave', handleMouseUp);
    }

    function handleMouseMove(event) {
        if (!drawing) return;

        // For window events, we need to calculate offset manually
        const currentX = event.clientX - canvas.offsetLeft;
        const currentY = event.clientY - canvas.offsetTop;

        // Call the correct drawing function based on the selected tool
        switch(tool) {
            case 'huabi':
                drawPen(lastX, lastY, currentX, currentY);
                break;
            case 'shuazi':
                drawBrush(lastX, lastY, currentX, currentY);
                break;
            case 'penqiang':
                // Spray gun effect is based on a single point
                drawSpray(currentX, currentY);
                break;
            case 'xiangpi':
                erase(lastX, lastY, currentX, currentY);
                break;
        }

        // Update last coordinates
        [lastX, lastY] = [currentX, currentY];
    }

    function handleMouseUp() {
        drawing = false;
        // CRITICAL: Remove all temporary listeners to prevent memory leaks
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
        window.removeEventListener('mouseleave', handleMouseUp);
    }

    // Attach the initial listener to the canvas
    canvas.addEventListener('mousedown', handleMouseDown);

    // --- Drawing Functions ---

    function drawPen(startX, startY, endX, endY) {
        ctx.beginPath();
        ctx.globalAlpha = 1;
        ctx.lineWidth = 2;
        ctx.strokeStyle = "#000";
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
    }

    function drawBrush(startX, startY, endX, endY) {
        ctx.beginPath();
        ctx.globalAlpha = 1;
        ctx.lineWidth = 10;
        ctx.strokeStyle = "#000";
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
    }

    function drawSpray(x, y) {
        for(let i = 0; i < 15; i++){
            const randomAngle = Math.random() * 2 * Math.PI;
            const randomRadius = Math.random() * 15;
            const sprayX = x + randomRadius * Math.cos(randomAngle);
            const sprayY = y + randomRadius * Math.sin(randomAngle);

            ctx.fillStyle = '#000';
            ctx.beginPath();
            ctx.globalAlpha = 0.5;
            ctx.arc(sprayX, sprayY, 1, 0, 2 * Math.PI);
            ctx.fill();
        }
    }

    function erase(startX, startY, endX, endY) {
        ctx.beginPath();
        ctx.globalAlpha = 1; // Eraser should be fully opaque

        if (eraserShape === 'rect') {
            // Use clearRect for rectangular erasing for performance
            // This implementation uses stroking to show the concept
            ctx.lineWidth = eraserSize;
            ctx.strokeStyle = "#FFFFFF"; // Erase by drawing with white
            ctx.moveTo(startX, startY);
            ctx.lineTo(endX, endY);
            ctx.stroke();
        } else { // 'circle'
            ctx.fillStyle = "#FFFFFF";
            ctx.arc(startX, startY, eraserSize / 2, 0, 2 * Math.PI);
            ctx.fill();
        }
    }
})();
    </script>
</body>
</html>
```

我对代码做了扩展，除了支持画笔，还支持喷枪、刷子、橡皮擦功能。
### canvas 转成图片
将 canvas 转成图片，需要用到以下属性：
* toDataURL

canvas.toDataURL() 方法返回一个包含图片展示的 data URI 。可以使用 type 参数其类型，默认为 PNG 格式。图片的分辨率为96dpi。

```js
const image = new Image()
// canvas.toDataURL 返回的是一串Base64编码的URL
image.src = canvas.toDataURL("image/png")
```
