import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../ui/Button';
import { motion } from 'framer-motion';

export function HeroSection() {
  const navigate = useNavigate();

  return (
    <div className="relative isolate pt-14 pb-8 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mx-auto max-w-2xl text-center"
      >
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl mb-8">
          Transform Your Images into Professional Embroidery Files
        </h1>
        
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="relative mx-auto w-full max-w-xl mb-12"
        >
          <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-40 h-40 bg-indigo-100 rounded-full blur-3xl opacity-30"></div>
          <img
            src="https://images.unsplash.com/photo-1620799140188-3b2a02fd9a77?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"
            alt="Embroidery Preview"
            className="w-full rounded-xl shadow-2xl"
          />
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-6 text-lg leading-8 text-gray-600 mb-8"
        >
          Advanced AI technology that converts your images into high-quality embroidery files, 
          ready for any machine. Perfect for both hobbyists and professionals.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Button size="lg" onClick={() => navigate('/signup')}>
            Get Started
          </Button>
          <Button variant="outline" size="lg" onClick={() => navigate('/pricing')}>
            View Pricing
          </Button>
        </motion.div>
      </motion.div>
    </div>
  );
}


// import React from 'react';
// import { useNavigate } from 'react-router-dom';
// import { Button } from '../ui/Button';
// import { motion } from 'framer-motion';

// export function HeroSection() {
//   const navigate = useNavigate();

//   return (
//     <div className="relative isolate pt-14 pb-8 lg:px-8">
//       <div className="absolute inset-x-0 overflow-hidden -top-40 -z-10 transform-gpu blur-3xl sm:-top-80">
//         <div className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]" />
//       </div>

//       <motion.div
//         initial={{ opacity: 0, y: 20 }}
//         animate={{ opacity: 1, y: 0 }}
//         transition={{ duration: 0.6 }}
//         className="mx-auto max-w-2xl text-center"
//       >
//         <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl mb-8">
//           Transform Your Images into Professional Embroidery Files
//         </h1>
        
//         <motion.div
//           initial={{ opacity: 0, scale: 0.8 }}
//           animate={{ opacity: 1, scale: 1 }}
//           transition={{ delay: 0.3, duration: 0.5 }}
//           className="relative mx-auto w-full max-w-xl mb-12 group"
//         >
//           <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl blur opacity-25 group-hover:opacity-75 transition duration-1000"></div>
//           <div className="relative">
//             <div className="aspect-[16/9] rounded-xl bg-gray-900/5 p-2">
//               <img
//                 src="https://images.unsplash.com/photo-1620799140188-3b2a02fd9a77?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"
//                 alt="Embroidery Preview"
//                 className="w-full h-full object-cover rounded-lg shadow-2xl ring-1 ring-gray-900/10"
//               />
//               <div className="absolute inset-0 rounded-lg bg-gradient-to-t from-gray-900/50 to-transparent flex items-end justify-center p-8">
//                 <div className="text-white text-center">
//                   <p className="text-lg font-semibold mb-2">Powered by AI</p>
//                   <p className="text-sm opacity-75">Advanced algorithms for precise embroidery conversion</p>
//                 </div>
//               </div>
//             </div>
//           </div>
//         </motion.div>

//         <motion.p
//           initial={{ opacity: 0 }}
//           animate={{ opacity: 1 }}
//           transition={{ delay: 0.6 }}
//           className="mt-6 text-lg leading-8 text-gray-600 mb-8"
//         >
//           Advanced AI technology that converts your images into high-quality embroidery files, 
//           ready for any machine. Perfect for both hobbyists and professionals.
//         </motion.p>

//         <motion.div
//           initial={{ opacity: 0, y: 20 }}
//           animate={{ opacity: 1, y: 0 }}
//           transition={{ delay: 0.8 }}
//           className="flex flex-col sm:flex-row items-center justify-center gap-4"
//         >
//           <Button size="lg" onClick={() => navigate('/signup')}>
//             Get Started
//           </Button>
//           <Button variant="outline" size="lg" onClick={() => navigate('/pricing')}>
//             View Pricing
//           </Button>
//         </motion.div>
//       </motion.div>

//       <div className="absolute inset-x-0 top-[calc(100%-13rem)] -z-10 transform-gpu overflow-hidden blur-3xl sm:top-[calc(100%-30rem)]">
//         <div className="relative left-[calc(50%+3rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30 sm:left-[calc(50%+36rem)] sm:w-[72.1875rem]" />
//       </div>
//     </div>
//   );
// }