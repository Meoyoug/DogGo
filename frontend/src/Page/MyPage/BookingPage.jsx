import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import axios from "../../api/axios";
import "./BookingPage.css";

const BookingPage = () => {
  const [booking, setBooking] = useState(null);
  const [formData, setFormData] = useState({});
  const [selectedCoupon, setSelectedCoupon] = useState(null);
  const location = useLocation();

  const [numberOfPeople, setNumberOfPeople] = useState(1);
  const [smallPetsCount, setSmallPetsCount] = useState(0);
  const [mediumPetsCount, setMediumPetsCount] = useState(0);
  const [largePetsCount, setLargePetsCount] = useState(0);

  const PersonToTalPrice = numberOfPeople * 15000;
  const smallPetsTotalPrice = smallPetsCount * 6000;
  const mediumPetsTotalPrice = mediumPetsCount * 10000;
  const largePetsTotalPrice = largePetsCount * 15000;
  const [selected, setSelected] = useState(0);
  const [totalPrice, setTotalPrice] = useState(0);
  useEffect(() => {
    setTotalPrice(
      PersonToTalPrice +
        smallPetsTotalPrice +
        mediumPetsTotalPrice +
        largePetsTotalPrice
    );
  }, [numberOfPeople, smallPetsCount, mediumPetsCount, largePetsCount]);

  const handleNumberOfPeopleChange = (amount) => {
    setNumberOfPeople((prevCount) => Math.max(1, prevCount + amount));
  };

  const handleSmallPetsChange = (amount) => {
    setSmallPetsCount((prevCount) => Math.max(0, prevCount + amount));
  };

  const handleMediumPetsChange = (amount) => {
    setMediumPetsCount((prevCount) => Math.max(0, prevCount + amount));
  };

  const handleLargePetsChange = (amount) => {
    setLargePetsCount((prevCount) => Math.max(0, prevCount + amount));
  };

  const [couponInfo, setCouponInfo] = useState([]);
  const [loading, setLoading] = useState(true);

  const getCouponInfo = async () => {
    try {
      const response = await axios.get("/api/v1/coupon/mycoupon", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (response.status === 200) {
        const data = response.data;
        setCouponInfo(data);
      }
    } catch (error) {
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    getCouponInfo();
  }, []);

  useEffect(() => {
    const fetchBooking = async () => {
      try {
        const response = await axios.get(`/api/v1/order/${location.state.id}`);
        setBooking(response.data);
      } catch (error) {}
    };

    fetchBooking();
  }, [location.state.id]);
  const handleSelectChange = (e) => {
    setSelected(e.target.value);
  };
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const requestBody = {
        user_coupon_id: selected ? selected.id : 0,
        people: numberOfPeople,
        pet_size_small: smallPetsCount,
        pet_size_medium: mediumPetsCount,
        pet_size_big: largePetsCount,
        departure_date: booking.departure_date,
      };

      await axios.put(`/api/v1/order/${booking.order_id}`, requestBody);

      alert("예약 정보가 성공적으로 업데이트되었습니다.");
    } catch (error) {}
  };

  const handlePayment = () => {
    window.location.href = "/paymentpage";
  };

  const handleCouponSelect = (coupon) => {
    setSelectedCoupon(coupon);
    setFormData({ ...formData, coupon: coupon ? coupon.id : null });
  };

  return (
    <div className="booking_page_title">
      {booking ? (
        <>
          <div className="booking_page">
            <div className="booking_edit">
              <h2>{booking.product.name}</h2>
              <form onSubmit={handleSubmit}>
                <div className="booking_check">
                  <label>인원</label>
                  <div className="booking_check">
                    <button
                      type="button"
                      onClick={() => handleNumberOfPeopleChange(-1)}
                    >
                      -
                    </button>
                    <span> {numberOfPeople} </span>
                    <button
                      type="button"
                      onClick={() => handleNumberOfPeopleChange(1)}
                    >
                      +
                    </button>
                  </div>
                </div>
                <div className="booking_check">
                  <label>소형</label>
                  <div className="booking_check">
                    <button
                      type="button"
                      onClick={() => handleSmallPetsChange(-1)}
                    >
                      -
                    </button>
                    <span> {smallPetsCount} </span>
                    <button
                      type="button"
                      onClick={() => handleSmallPetsChange(1)}
                    >
                      +
                    </button>
                  </div>
                </div>
                <div className="booking_check">
                  <label>중형</label>
                  <div className="booking_check">
                    <button
                      type="button"
                      onClick={() => handleMediumPetsChange(-1)}
                    >
                      -
                    </button>
                    <span> {mediumPetsCount} </span>
                    <button
                      type="button"
                      onClick={() => handleMediumPetsChange(1)}
                    >
                      +
                    </button>
                  </div>
                </div>
                <div className="booking_check">
                  <label>대형</label>
                  <div className="booking_check">
                    <button
                      type="button"
                      onClick={() => handleLargePetsChange(-1)}
                    >
                      -
                    </button>
                    <span> {largePetsCount} </span>
                    <button
                      type="button"
                      onClick={() => handleLargePetsChange(1)}
                    >
                      +
                    </button>
                  </div>
                </div>
                <div>
                  <p>쿠폰 사용여부</p>
                  <select
                    value={selected}
                    onChange={(e) => handleSelectChange(e)}
                  >
                    <option value={0}>선택안함</option>
                    {couponInfo.map((coupon) => (
                      <option
                        key={coupon.id}
                        value={coupon.coupon_info.sale_price}
                      >
                        {coupon.coupon_info.content}
                      </option>
                    ))}
                  </select>
                </div>
              </form>
            </div>
            <hr />
            <div className="booking_page_info">
              <div className="booking_container">
                <img
                  className="booking_img"
                  src={booking.product.product_img}
                  alt="상품 이미지"
                />
                <div className="booking_info_data">
                  <h3>예약일 : {booking.departure_date}</h3>
                  <h3>인원: {numberOfPeople}명 </h3>
                  <hr />
                  <h4>댕댕이 정보</h4>

                  <p style={{ fontSize: "20px" }}>소형 :{smallPetsCount}마리</p>
                  <p style={{ fontSize: "20px" }}>
                    중형 : {mediumPetsCount}마리
                  </p>
                  <p style={{ fontSize: "20px" }}>
                    대형 : {largePetsCount}마리
                  </p>
                  <hr />
                  <h3>
                    할인 적용 :{selected !== "0" ? "-" : ""} ₩
                    {Number(selected).toLocaleString()}원
                  </h3>
                  {selectedCoupon && (
                    <h3>선택한 쿠폰: {selectedCoupon.coupon_info.content}</h3>
                  )}
                  <h2>
                    결제 금액 : ₩
                    {`${(
                      booking.total_price +
                      totalPrice -
                      Number(selected)
                    ).toLocaleString()}`}
                    원
                  </h2>
                </div>
              </div>
            </div>
          </div>
          <hr />
          <div className="booking_button">
            <button type="submit" onClick={handleSubmit}>
              예약 정보 수정
            </button>
            <button onClick={handlePayment}>결제 페이지로</button>
          </div>
          <hr />
        </>
      ) : (
        <p>예약 정보를 불러오는 중입니다...</p>
      )}
    </div>
  );
};

export default BookingPage;
