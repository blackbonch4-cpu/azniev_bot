import './CourseCard.css'

function CourseCard({ webinar, onClick }) {
  const defaultImage = 'https://via.placeholder.com/300x300?text=Курс'

  return (
    <div className="course-card" onClick={() => onClick(webinar)}>
      <div
        className="course-card-image"
        style={{ backgroundImage: `url(${webinar.image_url || defaultImage})` }}
      >
        {webinar.is_purchased && (
          <div className="course-badge">✓ Куплено</div>
        )}
      </div>
      <div className="course-card-info">
        <div className="course-card-title">{webinar.title}</div>
        <div className="course-card-price">{webinar.price} ₽</div>
      </div>
    </div>
  )
}

export default CourseCard
