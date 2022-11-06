import styles from './styles.module.scss'
import React, { useRef, useState, useEffect } from 'react';
import Image from 'next/image';
import Slider from '@mui/material/Slider';
import PauseRounded from '@mui/icons-material/PauseRounded';
import PlayArrowRounded from '@mui/icons-material/PlayArrowRounded';
import FastForwardRounded from '@mui/icons-material/FastForwardRounded';
import FastRewindRounded from '@mui/icons-material/FastRewindRounded';
import IconButton from '@mui/material/IconButton';
import { useTheme } from '@mui/material/styles';
import SearchButton from "../search-button"
import axios from 'axios'
import SnackBar from '../../general/snack-bar/snack-bar'



function VideoPlayer() {
    const videoRef = useRef(null);
    const [duration, setDuration] = useState(0);

    const [showVideo, setShowVideo] = useState(false);
    const [showImg, setShowImg] = useState(false);
    const [videoSrc, setVideoSrc] = useState('')
    const [videoPath, setVideoPath] = useState('')
    const [imgSrc, setImgSrc] = useState('')
    const [tracks, setTracks] = useState([])
    const [searchLoading, setSearchLoading] = useState(false)
    const [snackBarState, setSnackBarState] = useState('closed')
    const [loadingPercent, setLoadingPercent] = useState(0)

    const videoInputRef = useRef(null)
    const imageInputRef = useRef(null)

    const trackRef = useRef(null);
    const theme = useTheme();

    const [playing, setPlaying] = useState(false);
    useEffect(() => {
        if (!videoRef.current) return

        if (playing) {
            videoRef.current.play();
        } else {
            videoRef.current.pause();
        }
    }, [playing]);

    const [position, setPosition] = useState(0);
    const handleCurrentTime = (value) => {
        if (videoRef.current) videoRef.current.currentTime = value;
    }
    const fastForward = () => {
        if (!videoRef.current) return

        videoRef.current.currentTime += 5;
        setPosition(videoRef.current.currentTime);
    };
    const revert = () => {
        if (!videoRef.current) return

        videoRef.current.currentTime -= 5;
        setPosition(videoRef.current.currentTime);
    };



    useEffect(() => {
        if (!videoRef.current) return
        const interval = window.setInterval(function () {
            setPosition(videoRef.current?.currentTime);
        }, 1000);
        // Clearing the interval to stop react memory leak error when component is unmounted
        return () => {
            window.clearInterval(interval);
        }
    }, [showVideo])

    return (
        <>
            <div className={`${styles["row"]} ${styles['upload-box']}`}>
                <div className={styles["video-container"]}>

                    <input type="file" className='d-none' id='video-input' ref={videoInputRef} onChange={function (e) {
                        setVideoPath(videoInputRef.current.files[0].path)
                        setVideoSrc(URL.createObjectURL(videoInputRef.current.files[0]))
                        setShowVideo(true)
                    }} />
                    {videoSrc.length === 0 ? (<label htmlFor="video-input">
                        <div className={styles['video-upload']}>
                            <span className={`material-icons ${styles["material-icons"]}`}>
                                file_upload
                            </span>
                        </div>
                    </label>
                    ) :
                        (
                            <video
                                ref={videoRef}
                                className={styles["video-" + showVideo]}
                                autoPlay={false}
                                loop={false}
                                playsInline={true}
                                muted={true}
                                controls={false}
                                src={videoSrc}
                                // Using this callback ensures that the video is loaded before we can get the duration.
                                // Using useEffect causes NaN for the duration when coming back from another page.
                                onLoadedMetadata={() => {
                                    setDuration(videoRef.current.duration)
                                }}
                            />)
                    }
                </div>
                {/* Subject Image */}
                <div className={styles['subject-image-container']}>

                    <input type="file" className='d-none' id='image-input' ref={imageInputRef} onChange={function (e) {
                        setImgSrc(imageInputRef.current.files[0].path)
                        setShowImg(true)
                    }} />

                    {imgSrc.length === 0 ?
                        (<label htmlFor="image-input">
                            <div className={styles['image-upload']}>
                                <span className={`material-icons ${styles["material-icons"]}`}>
                                    file_upload
                                </span>
                            </div>
                        </label>
                        ) :
                        (<Image
                            className={`${styles["image-" + showImg]} ${styles['subject-image']}`}
                            src={URL.createObjectURL(imageInputRef.current.files[0])}
                            alt="search-subject"
                            layout='fill' />)
                    }
                </div>
            </div>
            {/* Video track */}
            <Slider
                aria-label="time-indicator"
                size="small"
                value={position}
                min={0}
                step={0.01}
                max={duration}
                onChange={(_, value) => {
                    if (duration !== 0) {
                        handleCurrentTime(value);
                    }
                    setPosition(value)
                }}
                sx={{
                    color: theme.palette.mode === 'dark' ? '#fff' : 'rgba(0,0,0,0.87)',
                    height: 4,
                    marginTop: '24px',
                    '& .MuiSlider-thumb': {
                        width: 8,
                        height: 8,
                        transition: '0.3s cubic-bezier(.47,1.64,.41,.8)',
                        '&:before': {
                            boxShadow: '0 2px 12px 0 rgba(0,0,0,0.4)',
                        },
                        '&:hover, &.Mui-focusVisible': {
                            boxShadow: `0px 0px 0px 8px ${theme.palette.mode === 'dark'
                                ? 'rgb(255 255 255 / 16%)'
                                : 'rgb(0 0 0 / 16%)'
                                }`,
                        },
                        '&.Mui-active': {
                            width: 20,
                            height: 20,
                        },
                    },
                    '& .MuiSlider-rail': {
                        opacity: 0.28,
                    },
                }}
            />
            {/* Video time */}
            <div>{Math.floor(position / 60) + ":" + Math.floor(position % 60)}</div>

            {/* Controls */}
            <div className="flex-center">
                <IconButton aria-label="previous song" onClick={revert}>
                    <FastRewindRounded fontSize="large" htmlColor={"#000"} />
                </IconButton>
                <IconButton
                    aria-label={playing ? 'pause' : 'play'}
                    onClick={() => setPlaying(!playing)}
                >
                    {!playing ? (
                        <PlayArrowRounded
                            sx={{ fontSize: '3rem' }}
                            htmlColor={"#000"}
                        />
                    ) : (
                        <PauseRounded sx={{ fontSize: '3rem' }} htmlColor={"#000"} />
                    )}
                </IconButton>
                <IconButton aria-label="next song" onClick={fastForward}>
                    <FastForwardRounded fontSize="large" htmlColor={"#000"} />
                </IconButton>
            </div>

            {/* Ranges */}
            <div className={styles["ranges"]}>
                <div className={styles['track']} ref={trackRef}>
                    {tracks.map((track, index) => (
                        <div className={styles["range"]} key={index} style={
                            {
                                left: trackRef.current ? (track[0] * trackRef.current?.offsetWidth) / duration : 0,
                                width: (function () {
                                    const t = (track[1] - track[0])
                                    if (t < 0.3) {
                                        return ((0.3 * trackRef.current?.offsetWidth) / duration);
                                    }
                                    else {
                                        return ((t * trackRef.current?.offsetWidth) / duration)
                                    }
                                })()
                            }
                        }>
                        </div>
                    ))}
                    {/* <div className={styles["range"]} style={
                        {
                            left: trackRef.current && duration ? (5 * trackRef.current?.offsetWidth) / duration : 0,
                            width: trackRef.current && duration ? (5 * trackRef.current?.offsetWidth) / duration : 0
                        }
                    }>
                    </div>
                    <div className={styles["range"]} style={
                        {
                            left: trackRef.current && duration ? (trackRef.current?.offsetWidth * 30) / duration : 0,
                            width: trackRef.current && duration ? (trackRef.current?.offsetWidth * 20) / duration : 0
                        }
                    }>
                    </div> */}
                </div>
            </div>

            <SearchButton loading={searchLoading} loadingPercent={loadingPercent} disabled={!(videoSrc.length !== 0 && imgSrc.length !== 0)} onClick={videoSrc.length !== 0 && imgSrc.length !== 0 ? async () => {
                setSearchLoading(true)
                setSnackBarState('closed')
                try {
                    // let res = await axios.post('http://0.0.0.0:5000/face_search', {
                    //     "vid_pth": videoPath,
                    //     "img_pth": imgSrc
                    // })
                    // setTracks(res.data?.result || [])
                    // console.log(res.data);
                    const webSocket = new WebSocket("ws://localhost:4444");
                    webSocket.onopen = () => {
                        // console.log('open');
                        webSocket.send(imgSrc)
                        webSocket.send(videoPath)

                    }

                    webSocket.onmessage = (result) => {
                        const data = JSON.parse(result.data)
                        if (typeof data === "number") setLoadingPercent(data)
                        else {
                            console.log(data);
                            setTracks(data.result || [])
                            webSocket.close()
                            setSearchLoading(false)
                            return
                        }
                    }
                }
                catch (e) {
                    console.log(e);
                    setSnackBarState('open')
                    setSearchLoading(false)
                }
            } : () => { }} />

            <SnackBar
                text='An error occured'
                type='error'
                snackBarState={snackBarState}
                setSnackBarState={setSnackBarState} />

        </>
    );
}

export default VideoPlayer;
