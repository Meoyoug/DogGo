import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import './index.css';

function Modal({ isOpen, onClose, children }) {
    if (!isOpen) return null;
    
    return (
    <div className="paymentpage-modal-overlay">
        <div className="paymentpage-modal">
        <div className="paymentpage-modalclose-btn">
        <button
        onClick={onClose}
        >
        x
        </button>
        </div>
        <p>이 패키지의 최대 인원은 4명(유아 제외)입니다.
        반려동물은 최소 1마리 이상 포함되어야 합니다.</p>
            {children}
        <button
        onClick={onClose}
        className="paymentpage-modalclose-btn2"
        >
        취소
        </button>
        </div>
    </div>
    );
}

function PaymentPage() {
    const location = useLocation();
    const travelData = location.state.travelData;
    const posttravelData = location.state.posttravelData;
    const totalPricepay = location.state.totalPrice;

    const [departureDate, setDepartureDate] = useState("");
    const [numberOfPeople, setNumberOfPeople] = useState(posttravelData.numberOfPeople);
    const [smallPetsCount, setSmallPetsCount] = useState(posttravelData.smallPetsCount);
    const [mediumPetsCount, setMediumPetsCount] = useState(posttravelData.mediumPetsCount);
    const [largePetsCount, setLargePetsCount] = useState(posttravelData.largePetsCount);

    const [showPaymentInputs, setShowPaymentInputs] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const handlePayment = (e) => {
    e.preventDefault();
    console.log("출발일:", departureDate);
    console.log("인원수:", numberOfPeople);
    console.log("소 반려동물 수:", smallPetsCount);
    console.log("중 반려동물 수:", mediumPetsCount);
    console.log("대 반려동물 수:", largePetsCount);
};

const totalPrice = () => {
    const basePrice = totalPricepay;
    const personPrice = numberOfPeople * 15000;
    const smallPetPrice = smallPetsCount * 6000;
    const mediumPetPrice = mediumPetsCount * 10000;
    const largePetPrice = largePetsCount * 15000;
    return basePrice + personPrice + smallPetPrice + mediumPetPrice + largePetPrice;
  };

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

  const togglePaymentInputs = () => {
    setShowPaymentInputs((prev) => !prev);
  };

  const toggleModal = () => {
    setIsModalOpen((prev) => !prev);
  };

  const handleSubmitChanges = () => {
    toggleModal();
    setShowPaymentInputs(false);
    
  };

  return (
    <div className="paymentpage-container">
      <div className="paymentpage-des">
        {travelData ? (
          <div>
            <h2>{travelData.name}</h2>
            <img 
              src={travelData.product_img}
              alt="상품 이미지"
              className="paymentpage-img"
            />
            <hr />
            <h4>상세요금</h4>
            <h5>패키지 요금<span>₩{Number(travelData.price).toLocaleString()}원</span></h5>
            <h5>추가 인원<span>₩{((numberOfPeople * 15000)).toLocaleString()}원</span></h5>
            <h5>추가 반려견<span>₩{((smallPetsCount * 6000) + (mediumPetsCount * 10000) + (largePetsCount * 15000)).toLocaleString()}원</span></h5>
            <hr />
            <h5>총 합계(KRW) <span>₩{totalPrice().toLocaleString()}원</span></h5>
          </div>
        ) : (
          <p>상품 정보를 불러오는 중입니다...</p>
        )}
      </div>

      <form onSubmit={handlePayment}
      className="paymentpage-form">
        <h2>확인 및 결제</h2>
        <h3>예약정보</h3>
        <label>출발일</label>
        <input
          type="date"
          id="departureDate"
          value={departureDate}
          onChange={(e) => setDepartureDate(e.target.value)}
        />
        
        <div className="paymentpage-input">
          <div className="paymentpage-totalprice">
            <p>인원 / 반려동물</p>
            <p>{numberOfPeople}명 / {smallPetsCount + mediumPetsCount + largePetsCount} 마리
              <button type="button" onClick={toggleModal}>
                수정하기
              </button>
            </p>
          </div>
        </div>
        <hr />
        <h4>예약하려면 로그인 또는 회원 가입하세요.<Link to="/login" className="paymentpage-totalprice-link">로그인</Link></h4>
        <div className="paymentpage-form-totalpaybtn">
        <button type="submit">결제하기</button>
        <div class="hr-sect">또는</div>
        </div>
        <div className="paymentpage-other-login">
        <a href="네이버 OAuth 인증 URL" className="login-link">
        네이버 로그인
        </a>
        <a href="구글 OAuth 인증 URL" className="login-link">
        구글 로그인
        </a>
        <a href="카카오 OAuth 인증 URL" className="login-link">
        카카오 로그인
        </a>
        </div>
        </form>

    
      <Modal 
      isOpen={isModalOpen} 
      onClose={toggleModal}
      className='paymentpage-check-modal'>
            <div className="paymentpage-check">
            <label>인원 수</label>
            <div className="paymentpage-check_control">
            <button type="button" onClick={() => handleNumberOfPeopleChange(-1)}>-</button>
            <span> {numberOfPeople} 명</span>
            <button type="button" onClick={() => handleNumberOfPeopleChange(1)}>+</button>
            </div>
        </div>
        <div className="paymentpage-check">
                <label>반려동물 소</label>
                <div className="paymentpage-check_control">
                    <button type="button" onClick={() => handleSmallPetsChange(-1)}>-</button>
                    <span>{smallPetsCount} 마리</span>
                    <button type="button" onClick={() => handleSmallPetsChange(1)}>+</button>
                </div>
                </div>
                
        <div className="paymentpage-check">
            <label>반려동물 중</label>
            <div className="paymentpage-check_control">
                <button type="button" onClick={() => handleMediumPetsChange(-1)}>-</button>
                <span>{mediumPetsCount} 마리</span>
                <button type="button" onClick={() => handleMediumPetsChange(1)}>+</button>
            </div>
            </div>

            <div className="paymentpage-check">
                <label>반려동물 대</label>
                <div className="paymentpage-check_control">
                <button type="button" onClick={() => handleLargePetsChange(-1)}>-</button>
                <span>{largePetsCount} 마리</span>
                <button type="button" onClick={() => handleLargePetsChange(1)}>+</button>
                </div>
            </div>
            <hr />
            <div className="paymentpage-check-storage">
            <button onClick={handleSubmitChanges}>저장</button>
            </div>
    </Modal>
    </div>
  );
}

export default PaymentPage;
