let game = null;
let gameThisRef = null;
let aiScreenInterval = null;
let botSocket = null
const aiScreenMilliseconds = 500;
const aiPort = parseInt(JSON.parse(document.getElementById('aiport').textContent))
const isAi = Number.isInteger(aiPort)

//
const socket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/game/clicks/'
);

socket.onopen = function(e) {
    const canvas = document.getElementById('canvas_initial');
    const config = {
        type: Phaser.WEBGL,
        width: 400,
        height: 300,
        scene: {
            preload: preload,
            create: create,
            update: update
        },
	canvas: canvas
    };

    game = new Phaser.Game(config);
};

socket.onerror = function(e) {
    console.log('onerror()');
};

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    // reward data
    if(typeof data.reward !== 'undefined') {

        // forward reward to AI
        if(isAi) {
            botSocket.send(JSON.stringify({
                'type': 'reward',
                'value': data.reward
            }))
        }
    }

    // x,y data
    else {
        gameThisRef.add.circle(data.x, data.y, 10, 0xffddbb);
    }
};

//
function preload() {
    //
}

function create() {
    gameThisRef = this;

    // ai player
    if(isAi) {
        botSocket = new WebSocket(
            'ws://'
            + 'localhost:'
            + aiPort
        )
    
        botSocket.onopen = e => {
            aiScreenInterval = setInterval(
                () => {
                    game.renderer.snapshot((e) => {
                        botSocket.send(JSON.stringify({
                            'type': 'snapshot',
                            'value': e.src
                        }))
                    })
                },
                aiScreenMilliseconds)
        }
    
        botSocket.onerror = e => {
            console.log('bot socket error')
        }
    
        botSocket.onmessage = e => {
            const data = JSON.parse(e.data)
            const funcName = data[0]
            const funcArgs = data.slice(1)
            window[funcName](...funcArgs)
        }
    }

    // human player
    else {
        this.input.on(
            'pointerdown',
            e => {
                apiClick(e.downX, e.downY)
            });
    }
}

function update() {
    //
}

//
function apiClick(x, y) {
    socket.send(JSON.stringify({
        'x': x,
        'y': y
    }))
}
