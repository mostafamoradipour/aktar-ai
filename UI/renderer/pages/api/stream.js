// import NextCors from 'nextjs-cors';
const Stream = require('node-rtsp-stream')
let stream;



export default async function handler(req, res) {
    // await NextCors(req, res, {
    //     // Options
    //     methods: ['GET', 'HEAD', 'PUT', 'PATCH', 'POST', 'DELETE'],
    //     origin: '*',
    //     optionsSuccessStatus: 200, // some legacy browsers (IE11, various SmartTVs) choke on 204
    // });
    if (req.body.url) {
        stream?.stop()
        stream = new Stream({
            name: 'name',
            streamUrl: req.body.url,
            // 'rtsp://localhost:8554/mystream',
            wsPort: 9999,
            ffmpegOptions: { // options ffmpeg flags
                '-stats': '', // an option with no neccessary value uses a blank string
                '-r': 30 // options with required values specify the value after the key
            }
        })
    }
    res.status(200).json({ stat: 'ok', url: req.body.url })

}