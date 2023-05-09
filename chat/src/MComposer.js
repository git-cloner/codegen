import React, {useCallback, useEffect, useImperativeHandle, useState} from 'react';
import AutoCompletion from "./AutoCompletion";

export default React.forwardRef((props, ref) => {
    const {onChange, onSend} = props;
    const [text, setText] = useState("");
    const [suggest, setSuggest] = useState([]);
    const [isSuggestShow, setSuggestShow] = useState(false);
    const [position, setPosition] = useState({left: "20px", bottom: "60px"}); //left, bottom
    const autoCompletionRef = React.useRef(null);

    useImperativeHandle(ref, () => ({
        setText,
    }));

    const showSuggestItems = useCallback((suggests) => {
        if (suggests.length > 0) {
            setSuggest(suggests);
            setSuggestShow(true);
        } else {
            setSuggestShow(false);
        }
    }, []);

    const handleChange = useCallback((ev) => {
        let val = ev.currentTarget.value;
        setText(val);
        onChange && onChange(val);

        //自动完成
        let suggests = [];
        if (val.length > 0) {
            suggests = ["aaaaa", "bbbbbb", "cccccc", "ddddddd", "eeeeeee"];
        }
        showSuggestItems(suggests);
    }, [showSuggestItems, onChange]);

    const send = useCallback((content) => {
        if (content) {
            onSend('text', content);
            setText('');
        }
        setSuggestShow(false);
    }, [onSend, setText]);

    const handleChoose = useCallback((suggest) => {
        if (suggest) {
            setText(suggest);
        }
        //不调用发送，用户可能需要修改选择的内容
        //send(suggest);
        setSuggestShow(false);
    }, [setText, send]);

    const handleSend = useCallback(() => {
        send(text)
    }, [send, text]);

    const handleKeydown = useCallback((e) => {
        let ret = false;
        if(isSuggestShow) {
            //只有在打开自动完成的时候交给自动完成接管事件
            ret = autoCompletionRef.current.onKeyEvent(e);
        }
        if (!ret) {
            if (!e.shiftKey && e.keyCode === 13) {
                send(text);
            }
        }
        if (!e.shiftKey && e.keyCode === 13) {
            e.preventDefault();
        }
    }, [send, text]);

    useEffect(() => {
        let node = document.getElementsByClassName("Composer")[0];
        setPosition({left: "20px", "bottom": node.clientHeight + "px"})
    }, []);
    return <>
        <AutoCompletion
            ref={autoCompletionRef}
            show={isSuggestShow}
            items={suggest}
            position={position}
            onChoose={handleChoose}/>
        <div className="Composer" ref={ref}>
            <div className="Composer-inputWrap">
                <div className="">
                        <textarea className="Input Input--outline Composer-input"
                                  placeholder="请输入您的问题，shift + 回车换行" rows="1"
                                  onKeyDown={handleKeydown}
                                  enterKeyHint="send" value={text} onChange={handleChange}></textarea></div>
            </div>
            {text && <div className="Composer-actions">
                <button className="Btn Btn--primary Composer-sendBtn" type="button" onClick={handleSend}>发送</button>
            </div>}
        </div>
    </>
});