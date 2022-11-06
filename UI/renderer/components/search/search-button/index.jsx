import styles from './styles.module.scss'
import ImageSearchIcon from '@mui/icons-material/ImageSearch';


export default function SearchButton({ onClick, loading, loadingPercent, disabled }) {

    return (
        <div className={styles['button-container']} onClick={onClick}>
            <button className={`${styles["btn"]} ${disabled ? styles['disabled'] : ''}`}>
                {loading ? (
                    <>
                        {loadingPercent}% Loading...
                    </>
                ) : (
                    <>
                        <ImageSearchIcon />
                        Run search
                    </>
                )}
            </button>
        </div>
    )
}
