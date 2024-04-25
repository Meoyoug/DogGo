import React from "react";
import { HiCursorClick } from "react-icons/hi";
import axios from "../../../api/axios";
import "./Main3.css";

function Main3() {
  const postCoupon = async () => {
    try {
      const response = await axios.post(`/api/v1/coupon/issue/1`,
        {}, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        }
      );
      console.log(response)
      if (response.status === 200) {
        console.log("쿠폰이 성공적으로 발급되었습니다!");
        alert("쿠폰이성공적으로 발급되었습니다!")
      } else {
        throw new Error("서버 응답 실패");
      }
    } catch (error) {
      console.log(error);
      console.log(error.response.data.msg)
      if (error.response.data.msg === 'already issued coupon.')
        alert("이미발급된쿠폰입니다.")
    }
  };

  return (
    <div className="Main3-contanier">
      <div className="image_box_01">
        <div className="WC">
          <button onClick={postCoupon}>₩50,000</button>
        </div>
        <div className="Main3-Click-deg">
          <span class="material-symbols-outlined Main3-Click"><HiCursorClick /></span>
        </div>
        <div className="WC2">
        </div>
      </div>
      <div className="image_box_02"></div>
      {/* <div className="image_box_03"></div> */}
    </div>
  );
}

export default Main3;
