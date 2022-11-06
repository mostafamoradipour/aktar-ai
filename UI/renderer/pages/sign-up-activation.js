import { useRouter } from 'next/router'
import axios from 'axios'
import Status from '@/components/activation/status'
import { useState, useEffect } from 'react'

export default function SignUpActivation() {
    const router = useRouter()
    const { token } = router.query

    const [status, setStatus] = useState(undefined)

    useEffect(() => {
        if (!router.isReady) return;
        axios
            .get("https://api.kachrobotics.com/api/user/set_csrf_cookie/", {
                withCredentials: true,
            })
            .then((res) => {
                let formData = new FormData();
                formData.append("csrfmiddlewaretoken", res.data["csrfmiddlewaretoken"]);
                formData.append("token", token);

                axios({
                    method: "post",
                    url: "https://api.kachrobotics.com/api/user/verify/",
                    data: formData,
                    headers: { "Content-Type": "multipart/form-data" },
                    withCredentials: true,
                })
                    .then((loginRes) => {
                        if (loginRes.data.status === "activated") {
                            setStatus(true)
                        }
                        else {
                            setStatus(false)
                        }
                    })
                    .catch((err) => {
                        setStatus(false)
                        // if (err.status === 400) {
                        // axios({
                        //     method: "post",
                        //     url: "https://api.kachrobotics.com/api/user/resend_verification_email/",
                        //     data: formData,
                        //     headers: { "Content-Type": "multipart/form-data" },
                        //     withCredentials: true,
                        // })
                        console.log('resend email')
                        // }
                    });
            })
        // .catch((err) => {
        //     // If CSRF check hasn’t been passed:
        //     // HTTP_403_FORBIDDEN
        //     setError("Error logging in... Please try again.");
        //     setSnackBarState("open");
        //     setAuthLoading(false);
        // });


    }, [router.isReady])

    return (
        <>
            {status !== undefined ?
                <Status passed={status} emailExists={false} />
                : <></>}
            <p>Please wait...</p>
            {/* TODO- make a better loading */}
        </>
    )

}
