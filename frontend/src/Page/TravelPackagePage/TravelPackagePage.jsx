import React, { useEffect, useState } from "react";
import request from "../../axios";
import Product from "./Product/Product";
import "./TravelPackagePage.css";

function Travelpackage() {
  const [products, setProducts] = useState([]);
  useEffect(() => {
    fetchProduct();
  }, []);

  const fetchProduct = async () => {
    try {
      const response = await request.get(`/api/v1/product/`, {
        headers: {
          "Content-Type": "application/json",
        },
        withCredentials: true,
      });

      if (response.status === 200) {
        setProducts(response.data);
      } else if (response.status === 404) {
      }
    } catch (error) {}
  };

  const [searchTerm, setSearchTerm] = useState(" ");

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const filteredProducts = products.filter((product) =>
    product.name.replace(/ /g, "").includes(searchTerm.replace(/ /g, ""))
  );

  return (
    <div className="petshop-page">
      <div className="petshop-page-title">
        <div className="petshop-page-title-title">
          <h1>
            Welcome to D<span>o</span>gG<span>O</span>!
          </h1>
          <p>도고에서 준비한 색다른 컨텐츠를 둘러보세요!</p>
          <input
            type="text"
            placeholder="검색어를 입력해주세요"
            value={searchTerm}
            onChange={handleSearchChange}
          />
        </div>
      </div>
      <div className="product-list-title"></div>
      <div className="product-list">
        {filteredProducts.map((products) => (
          <Product key={products.id} products={products} />
        ))}
      </div>
    </div>
  );
}

export default Travelpackage;
